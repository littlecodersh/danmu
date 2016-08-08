import time, socket, select, sys, re

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

class QuanMinDanMuClient(AbstractDanMuClient):
    def _prepare_env(self):
        r = requests.get('http://www.quanmin.tv/site/route?time='
                + str(int(time.time()))).content
        danmuIp = ''
        for i in range(4):
            danmuIp += str(ord(r[3 + 4*i])^172) + '.' # I tried many times and get 172
        danmuIp = danmuIp[:-1]
        roomId = self.url.split('/')[-1]
        if roomId.isdigit():
            roomInfo = {'uid': int(roomId), }
        else:
            url = '%s/%s/info.json?t=%s'%('http://www.quanmin.tv/json/rooms', 
                roomId, int(time.time() / 50))
            roomInfo = requests.get(url).json()
        return (danmuIp, 9098), ('0.0.0.0', 80), roomInfo # danmu, heart, roomInfo, success
    def _init_socket(self, danmu, heart, roomInfo):
        self.danmuSocket = _socket()
        self.danmuSocket.settimeout(3)
        roomId = roomInfo['uid']
        data = ('{\n' +
            '   "os" : 135,\n'
            '   "pid" : 10003,\n'
            '   "rid" : "%s",\n'
            '   "timestamp" : 78,\n'
            '   "ver" : 147\n}')%roomId
        # \x5e may have some problem
        data = '\x00\x00\x00\x5e' + data + '\x0a'
        self.danmuSocket.connect(danmu)
        self.danmuSocket.push(data)
    def _create_thread_fn(self, roomInfo):
        def get_danmu(self):
            if not select.select([self.danmuSocket], [], [], 1)[0]: return
            content = self.danmuSocket.pull()
            try:
                sender = [m.decode('unicode-escape').decode('unicode-escape') for m in re.findall('\\\\"nick\\\\":\\\\"(.*?)\\\\",\\\\"', content)]
                msg = [m.decode('unicode-escape').decode('unicode-escape') for m in re.findall('\\\\"text\\\\":\\\\"(.*?)\\\\",\\\\"', content)]
            except Exception, e:
                pass
            else:
                self.danmuWaitTime = time.time() + self.maxNoDanMuWait
                for m in zip(sender, msg): self.msgPipe.append(m)
        def heart_beat(self):
            time.sleep(3)
        return get_danmu, heart_beat # danmu, heart

if __name__ == '__main__':
    dc = QuanMinDanMuClient('http://www.quanmin.tv/star/1113774')
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
