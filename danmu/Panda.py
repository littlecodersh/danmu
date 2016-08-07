import time, sys, re
import socket, select

import requests

from Abstract import AbstractDanMuClient

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

class PandaDanMuClient(AbstractDanMuClient):
    def _prepare_env(self):
        roomId = self.url.split('/')[-1]
        url = 'http://www.panda.tv/ajax_chatroom?roomid=%s&_=%s'%(roomId, str(int(time.time())))
        roomInfo = requests.get(url).json()
        url = 'http://api.homer.panda.tv/chatroom/getinfo'
        params = {
            'rid': roomInfo['data']['rid'],
            'roomid': roomId,
            'retry': 0,
            'sign': roomInfo['data']['sign'], 
            'ts': roomInfo['data']['ts'],
            '_': int(time.time()), }
        serverInfo = requests.get(url, params).json()['data']
        serverAddress = serverInfo['chat_addr_list'][0].split(':')
        return (serverAddress[0], int(serverAddress[1])), ('0.0.0.0', 80), serverInfo
    def _init_socket(self, danmu, heart, roomInfo):
        data = [
            ('u', '%s@%s'%(roomInfo['rid'], roomInfo['appid'])),
            ('k', 1),
            ('t', 300),
            ('ts', roomInfo['ts']),
            ('sign', roomInfo['sign']),
            ('authtype', roomInfo['authType']) ]
        data = '\n'.join('%s:%s'%(k, v) for k, v in data)
        data = ('\x00\x06\x00\x02\x00' + chr(len(data)) +
            bytes(data.encode('utf8') + '\x00\x06\x00\x00'))
        self.danmuSocket = _socket(socket.AF_INET, socket.SOCK_STREAM)
        self.danmuSocket.settimeout(3)
        self.danmuSocket.connect(danmu)
        self.danmuSocket.push(data)
    def _create_thread_fn(self, roomInfo):
        def get_danmu(self):
            if not select.select([self.danmuSocket], [], [], 1)[0]: return
            content = self.danmuSocket.pull()
            try:
                sender = [m.decode('utf8', 'ignore').decode('unicode-escape') for m in re.findall('"nickName":"(.*?)","', content)]
                msg = [m.decode('utf8', 'ignore').decode('unicode-escape') for m in re.findall('"content":"(.*?)"}}', content)]
            except:
                pass
            else:
                self.danmuWaitTime = time.time() + self.maxNoDanMuWait
                for m in zip(sender, msg): self.msgPipe.append(m)
        def heart_beat(self):
            self.danmuSocket.push('\x00\x06\x00\x06')
            time.sleep(60)
        return get_danmu, heart_beat

if __name__ == '__main__':
    dc = PandaDanMuClient('http://www.panda.tv/88911')
    dc.start()
    print('Loaded')
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
        print len(dc.msgPipe)
