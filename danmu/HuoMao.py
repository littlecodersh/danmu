import socket, time, re, json, threading
from struct import pack

import requests

from .Abstract import AbstractDanMuClient

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

url = 'http://www.huomao.com/%s'
roomId = '1745'

c = requests.get(url % roomId).content
r = re.search('getFlash\("(.*?)","(.*?)"\);', c)
data = {
    'cid': r.group(1),
    'cdns': '1',
    'streamtype': 'live',
    'VideoIDS': r.group(2), }
j = requests.post('http://www.huomao.com/swf/live_data', data=data).json()
print(j['roomStatus'] == '1')

roomId = '11619'

url = 'http://chat.huomao.com/chat/getToken'
params = {
    'callback': 'jQuery171032695039477104815_1477741089191',
    'cid': roomId,
    '_': int(time.time() * 100), }
headers = { 'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 6.3; Win64; x64)'\
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36', }
c = requests.get(url, params=params, headers=headers).content
r = re.search('jQuery[^(]*?\((.*?)\)$', c)
if r:
    j = json.loads(r.group(1))['data']
    print(j)
else:
    raise Exception
s = socket.socket()
s.connect((j['host'], int(j['port'])))

def push_data(data, t=b'\x01'):
    data = t + pack('>I', len(data))[1:] + data
    print(repr(data))
    s.sendall(data)

data = {
    'user': None,
    'sys': {
        'version': '0.1.6b',
        'pomelo_version': '0.7.x',
        'type': 'pomelo-flash-tcp', }, }
data = json.dumps(data, separators=(',', ':'))
push_data(data)
print(repr(s.recv(999)))

s.sendall(b'\x02\x00\x00\x00')

data = {
    'channelId': roomId,
    'log': True,
    'userId': '', }
data = '\x00\x01\x20gate.gateHandler.lookupConnector'\
    + json.dumps(data, separators=(',', ':'))
push_data(data, b'\x04')
r = s.recv(999)[6:]
print(r)
newDes = json.loads(r)
print(newDes)
s = socket.socket()
s.connect((newDes['host'], newDes['port']))

def push_data(data, t=b'\x01'):
    data = t + pack('>I', len(data))[1:] + data
    print(repr(data))
    s.sendall(data)

data = {
    'user': None,
    'sys': {
        'version': '0.1.6b',
        'pomelo_version': '0.7.x',
        'type': 'pomelo-flash-tcp', }, }
data = json.dumps(data, separators=(',', ':'))
push_data(data)
print(repr(s.recv(999)))

s.sendall(b'\x02\x00\x00\x00')
s.recv(999)

data = {
    'channelId': roomId,
    'token': j['token'],
    'userId': j['uid'], }
data = json.dumps(data, separators=(',', ':'))
data = '\x00\x02\x20' + 'connector.connectorHandler.login' + data
push_data(data, b'\x04')
def heart_loop():
    while 1:
        time.sleep(30)
        s.sendall(b'\x03\x00\x00\x00')
t = threading.Thread(target=heart_loop)
t.setDaemon(True)
t.start()

while 1:
    r = s.recv(999)
    j = re.search(b'({".*?}$)', r)
    if j:
        j = json.loads(j.group(1).decode('utf8', 'replace'))
        if 'msg_content' not in j or 'msg_type' not in j: continue
        if j['msg_type'] == 'msg':
            print(j['msg_content'].get('content'))
        elif j['msg_type'] == 'beans':
            print(j['msg_content'].get('amount'))
    else:
        print(r)
