import socket, time, re, json, threading, select
from struct import pack

import requests

from .Abstract import AbstractDanMuClient

class _socket(socket.socket):
    def push(self, data, t=b'\x01'):
        data = t + pack('>I', len(data))[1:] + data
        self.sendall(data)
    def pull(self):
        try: # for socket.settimeout
            return self.recv(9999)
        except Exception as e:
            return ''

class HuoMaoDanMuClient(AbstractDanMuClient):
    def _get_live_status(self):
        c = requests.get(self.url).content
        r = re.search('getFlash\("(.*?)","(.*?)"\);', c)
        data = {
            'cid': r.group(1),
            'cdns': '1',
            'streamtype': 'live',
            'VideoIDS': r.group(2), }
        j = requests.post('http://www.huomao.com/swf/live_data', data=data).json()
        return j['roomStatus'] == '1'
    def _prepare_env(self):
        c = requests.get(self.url).content
        r = re.search('getFlash\("(.*?)","(.*?)"\);', c)
        roomId = r.group(1)
        url = 'http://chat.huomao.com/chat/getToken'
        params = {
            'callback': 'jQuery171032695039477104815_1477741089191',
            'cid': roomId,
            '_': int(time.time() * 100), }
        headers = { 'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 6.3; Win64; x64)'\
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36', }
        c = requests.get(url, params=params, headers=headers).content
        r = re.search('jQuery[^(]*?\((.*?)\)$', c)
        j = json.loads(r.group(1))['data']

        s = _socket()
        s.connect((j['host'], int(j['port'])))
        data = {
            'user': None,
            'sys': {
                'version': '0.1.6b',
                'pomelo_version': '0.7.x',
                'type': 'pomelo-flash-tcp', }, }
        data = json.dumps(data, separators=(',', ':'))
        s.push(data)
        s.pull()

        s.sendall(b'\x02\x00\x00\x00')

        data = {
            'channelId': roomId,
            'log': True,
            'userId': '', }
        data = '\x00\x01\x20gate.gateHandler.lookupConnector'\
            + json.dumps(data, separators=(',', ':'))
        s.push(data, b'\x04')
        r = s.pull()[6:]
        danmuPort = json.loads(r)

        return (danmuPort['host'], int(danmuPort['port'])),\
                {'roomId': roomId, 'token': j['token'], 'userId': j['uid']}
    def _init_socket(self, danmu, roomInfo):
        self.danmuSocket = _socket()
        self.danmuSocket.connect(danmu)
        self.danmuSocket.settimeout(3)

        data = {
            'user': None,
            'sys': {
                'version': '0.1.6b',
                'pomelo_version': '0.7.x',
                'type': 'pomelo-flash-tcp', }, }
        data = json.dumps(data, separators=(',', ':'))
        self.danmuSocket.push(data)
        self.danmuSocket.pull()

        self.danmuSocket.sendall(b'\x02\x00\x00\x00')
        self.danmuSocket.pull()

        data = {
            'channelId': roomInfo['roomId'],
            'token': roomInfo['token'],
            'userId': roomInfo['userId'], }
        data = json.dumps(data, separators=(',', ':'))
        data = '\x00\x02\x20' + 'connector.connectorHandler.login' + data
        self.danmuSocket.push(data, b'\x04')
    def _create_thread_fn(self, roomInfo):
        def keep_alive(self):
            time.sleep(30)
            self.danmuSocket.sendall(b'\x03\x00\x00\x00')
        def get_danmu(self):
            if not select.select([self.danmuSocket], [], [], 1)[0]: return
            content = self.danmuSocket.pull()
            for msg in re.findall(b'\x04\x00.*?({"[^\x04]*})', content):
                try:
                    msg = json.loads(msg.decode('utf8', 'ignore'))
                    if 'msg_content' not in msg or 'msg_type' not in msg: continue
                    msg['NickName'] = msg['msg_content']['username']
                    msg['Content']  = msg['msg_content'].get('content') or \
                        msg['msg_content'].get('amount')
                    msg['MsgType']  = {'msg': 'danmu', 'beans': 'gift',
                        'welcome': 'enter'}.get(msg.get('msg_type'), 'other')
                except Exception as e:
                    pass
                else:
                    self.danmuWaitTime = time.time() + self.maxNoDanMuWait
                    self.msgPipe.append(msg)
        return get_danmu, keep_alive # danmu, heart
