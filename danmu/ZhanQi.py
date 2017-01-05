import sys, json, time, re, base64
import socket, threading, select
from struct import pack

import requests

from danmu.config import USER_AGENT
from .Abstract import AbstractDanMuClient

class ZhanQiDanMuClient(AbstractDanMuClient):
    def _get_live_status(self):
        r = requests.get('https://www.zhanqi.tv/' +
            self.url.split('/')[-1] or self.url.split('/')[-2], 
            headers={'User-Agent': USER_AGENT})
        if r.url == 'https://www.zhanqi.tv/': return False
        rawJson = re.findall('oRoom = (.*);[\s\S]*?window.', r.text)
        if not rawJson: rawJson = re.findall('aVideos = (.*);[\s\S]*?oPageConfig.', r.text)
        self.roomInfo = json.loads(rawJson[0])
        if isinstance(self.roomInfo, list): self.roomInfo = self.roomInfo[0]
        return self.roomInfo['status'] == '4'
    def _prepare_env(self):
        serverAddress = json.loads(base64.b64decode(
            self.roomInfo['flashvars']['Servers']).decode('ascii'))['list'][0]
        serverAddress = (serverAddress['ip'], serverAddress['port'])
        url = '%s/api/public/room.viewer' % 'https://www.zhanqi.tv'
        params = {
            'uid': self.roomInfo['uid'],
            '_t': int(time.time() / 60), }
        roomInfo = requests.get(url, params).json()
        roomInfo['id'] = int(self.roomInfo['id'])
        return serverAddress, roomInfo # danmu, roomInfo
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
            for msg in re.findall(b'\x10\x27({[^\x00]*})\x0a', content):
                try:
                    msg = json.loads(msg.decode('utf8', 'ignore'))
                    msg['NickName'] = (msg.get('fromname', '') or
                        msg.get('data', {}).get('nickname', ''))
                    msg['Content']  = msg.get('content', '')
                    if 'chatm' in msg.get('cmdid', ''):
                        msg['MsgType'] = 'danmu'
                    elif 'Gift' in msg.get('cmdid', ''):
                        msg['MsgType'] = 'gift'
                    else:
                        msg['MsgType'] = 'other'
                except Exception as e:
                    pass
                else:
                    self.danmuWaitTime = time.time() + self.maxNoDanMuWait
                    self.msgPipe.append(msg)
        def heart_beat(self):
            time.sleep(3)
            self.danmuSocket.sendall(b'\xbb\xcc' + b'\x00'*8 + b'\x59\x27')
        return get_danmu, heart_beat # danmu, heart
