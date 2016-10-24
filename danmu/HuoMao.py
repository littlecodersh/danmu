import socket, time, re, json, threading
from struct import pack

import requests

roomId = '717'

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

s.sendall(b'\x02\x00\x00\x00\x04\x00\x00\x4d\x00\x01\x20')

data = {
    'channelId': roomId,
    'log': True,
    'userId': '', }
data = 'gate.gateHandler.lookupConnector'\
    + json.dumps(data, separators=(',', ':'))
s.sendall(data)
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
