import time, socket, select, sys, re, json
from struct import pack, unpack

import requests

from .Abstract import AbstractDanMuClient

class _socket(socket.socket):
    def communicate(self, data):
        self.push(data)
        return self.pull()
    def push(self, data):
        self.sendall(data)
    def pull(self):
        try: # for socket.settimeout
            return self.recv(9999)
        except:
            return ''

class QuanMinDanMuClient(AbstractDanMuClient):
    def _get_live_status(self):
        url = '%s/%s/info.json?t=%s' % ('http://www.quanmin.tv/json/rooms',
            self.url.split('/')[-1] or self.url.split('/')[-2], int(time.time() / 50))
        return requests.get(url).json()['play_status']
    def _prepare_env(self):
        r = requests.get('http://www.quanmin.tv/site/route?time='
                + str(int(time.time()))).content
        danmuIp = '.'.join([str(i ^ 172) for i in unpack('>iiii', r[:16])])
        roomId = self.url.split('/')[-1] or self.url.split('/')[-2]
        if roomId.isdigit():
            roomInfo = {'uid': int(roomId), }
        else:
            url = '%s/%s/info.json?t=%s'%('http://www.quanmin.tv/json/rooms', 
                roomId, int(time.time() / 50))
            roomInfo = requests.get(url).json()
        return (danmuIp, 9098), roomInfo # danmu, roomInfo, success
    def _init_socket(self, danmu, roomInfo):
        self.danmuSocket = _socket()
        self.danmuSocket.settimeout(3)
        roomId = roomInfo['uid']
        data = ('{\n' +
            '   "os" : 135,\n'
            '   "pid" : 10003,\n'
            '   "rid" : "%s",\n'
            '   "timestamp" : 78,\n'
            '   "ver" : 147\n}')%roomId
        data = pack('>i', len(data)) + data.encode('ascii') + b'\x0a'
        self.danmuSocket.connect(danmu)
        self.danmuSocket.push(data)
    def _create_thread_fn(self, roomInfo):
        def get_danmu(self):
            if not select.select([self.danmuSocket], [], [], 1)[0]: return
            content = self.danmuSocket.pull()
            for msg in re.findall(b'\x00\x00.*?({[^\x00]*)', content):
                try:
                    msg = json.loads(json.loads(msg.decode('ascii'))['chat']['json'])
                    msg['NickName'] = msg.get('user', {}).get('nick', '')
                    msg['Content']  = msg.get('text', '')
                    if msg.get('type') in (1,2,3,4,5):
                        msg['MsgType'] = 'gift'
                    elif msg.get('type') == 0:
                        msg['MsgType'] = 'danmu'
                    else:
                        msg['MsgType'] = 'other'
                except Exception as e:
                    pass
                else:
                    self.danmuWaitTime = time.time() + self.maxNoDanMuWait
                    self.msgPipe.append(msg)
        def heart_beat(self):
            time.sleep(3)
        return get_danmu, heart_beat # danmu, heart
