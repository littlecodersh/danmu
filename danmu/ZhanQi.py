import sys, json, time, re, base64
import socket, threading, select
from struct import pack

import requests

from .Abstract import AbstractDanMuClient

class ZhanQiDanMuClient(AbstractDanMuClient):
    def _prepare_env(self):
        baseUrl = 'http://www.zhanqi.tv'
        roomName = self.url.split('/')[-1]
        r = requests.get('%s/%s'%(baseUrl, roomName))
        if r.url == baseUrl: raise Exception('Wrong url')
        rawJson = re.findall('oRoom = (.*);[\s\S]*?window.bClose', r.text)
        if not rawJson: rawJson = re.findall('aVideos = (.*);[\s\S]*?oPageConfig.oUrl', r.text)
        roomInfo = json.loads(rawJson[0])
        if isinstance(roomInfo, list): roomInfo = roomInfo[0]
        roomId = int(roomInfo['id'])
        serverAddress = json.loads(base64.b64decode(roomInfo['flashvars']['Servers']).decode('ascii'))['list'][0]
        serverAddress = (serverAddress['ip'], serverAddress['port'])
        url = '%s/api/public/room.viewer'%baseUrl
        params = {
            'uid': roomInfo['uid'],
            '_t': int(time.time() / 60), }
        roomInfo = requests.get(url, params).json()
        roomInfo['id'] = roomId
        return serverAddress, roomInfo # danmu, roomInfo, success
    def _init_socket(self, danmu, roomInfo):
        self.danmuSocket = socket.socket()
        self.danmuSocket.settimeout(3)
        data = {
            'nickname'     : '',
            'roomid'       : int(roomInfo['id']),
            'gid'          : roomInfo['data']['gid'],
            'sid'          : roomInfo['data']['sid'],
            'ssid'         : roomInfo['data']['sid'],
            'timestamp'    : roomInfo['data']['timestamp'],
            'cmdid'        : 'loginreq',
            'develop_date' : '2015-06-07',
            'fhost'        : 'zhanqi.tool',
            'fx'           : 0,
            't'            : 0,
            'thirdacount'  : '',
            'uid'          : 0,
            'ver'          : 2,
            'vod'          : 0, }
        data = json.dumps(data, separators = (',',':'))
        self.danmuSocket.connect(danmu)
        self.danmuSocket.sendall(b'\xbb\xcc' + b'\x00'*4 +
            pack('i', len(data)) + b'\x10\x27' + data.encode('ascii'))
    def _create_thread_fn(self, roomInfo):
        def get_danmu(self):
            if not select.select([self.danmuSocket], [], [], 1)[0]: return
            content = self.danmuSocket.recv(999)
            try:
                sender = [m.decode('utf8', 'ignore') for m in re.findall(b'"fromname":"(.*?)"', content)]
                s = [m.decode('utf8', 'ignore') for m in re.findall(b'"content":"(.*?)"', content)]
            except Exception as e:
                pass
            else:
                self.danmuWaitTime = time.time() + self.maxNoDanMuWait
                for m in zip(sender, s): self.msgPipe.append(m)
        def heart_beat(self):
            time.sleep(3)
            self.danmuSocket.sendall(b'\xbb\xcc' + b'\x00'*8 + b'\x59\x27')
        return get_danmu, heart_beat # danmu, heart

if __name__ == '__main__':
    dc = ZhanQiDanMuClient('http://www.zhanqi.tv/9527')
    dc.start()
    print('Begin')
    def default_time_format(timeGap = 0):
        return time.strftime('%y%m%d-%H%M%S', time.localtime(time.time() + timeGap))
    try:
        while 1:
            if dc.msgPipe:
                with open('danmu.log', 'ab') as f: f.write((default_time_format()
                    + ' - ' + '[%s]: %s\n'%dc.msgPipe.pop()).encode('utf8'))
            else:
                time.sleep(.1)
    except:
        print(len(dc.msgPipe))
