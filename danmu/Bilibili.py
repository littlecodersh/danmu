import socket, json, re, select, time, random
from struct import pack

import requests

from .Abstract import AbstractDanMuClient

class _socket(socket.socket):
    def push(self, data, type = 7):
        data = (pack('>i', len(data) + 16) + b'\x00\x10\x00\x01' +
            pack('>i', type) + pack('>i', 1) + data)
        self.sendall(data)
    def pull(self):
        try: # for socket.settimeout
            return self.recv(9999)
        except Exception as e:
            return ''

class BilibiliDanMuClient(AbstractDanMuClient):
    def _get_live_status(self):
        url = ('http://live.bilibili.com/'
            + self.url.split('/')[-1] or self.url.split('/')[-2])
        self.roomId = re.findall(b'var ROOMID = (\d+);', requests.get(url).content)[0].decode('ascii')
        r = requests.get('http://live.bilibili.com/api/player?id=cid:' + self.roomId)
        self.serverUrl = re.findall(b'<server>(.*?)</server>', r.content)[0].decode('ascii')
        return re.findall(b'<state>(.*?)</state>', r.content)[0] == b'LIVE'
    def _prepare_env(self):
        return (self.serverUrl, 788), {}
    def _init_socket(self, danmu, roomInfo):
        self.danmuSocket = _socket()
        self.danmuSocket.connect(danmu)
        self.danmuSocket.settimeout(3)
        self.danmuSocket.push(data = json.dumps({
            'roomid': int(self.roomId),
            'uid': int(1e14 + 2e14 * random.random()),
            }, separators=(',', ':')).encode('ascii'))
    def _create_thread_fn(self, roomInfo):
        def keep_alive(self):
            self.danmuSocket.push(b'', 2)
            time.sleep(30)
        def get_danmu(self):
            if not select.select([self.danmuSocket], [], [], 1)[0]: return
            content = self.danmuSocket.pull()
            for msg in re.findall(b'\x00({[^\x00]*})', content):
                try:
                    msg = json.loads(msg.decode('utf8', 'ignore'))
                    msg['NickName'] = (msg.get('info', ['','',['', '']])[2][1]
                        or msg.get('data', {}).get('uname', ''))
                    msg['Content']  = msg.get('info', ['', ''])[1]
                    msg['MsgType']  = {'SEND_GIFT': 'gift', 'DANMU_MSG': 'danmu',
                        'WELCOME': 'enter'}.get(msg.get('cmd'), 'other')
                except Exception as e:
                    pass
                else:
                    self.danmuWaitTime = time.time() + self.maxNoDanMuWait
                    self.msgPipe.append(msg)
        return get_danmu, keep_alive # danmu, heart
