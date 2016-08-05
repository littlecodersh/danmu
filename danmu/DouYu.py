import socket, json, re, select, time

import requests

from Abstract import AbstractDanMuClient

class _socket(socket.socket):
    def communicate(self, data):
        self.push(data)
        return self.pull()
    def push(self, data):
        s = ''
        length = 9 + len(data)
        for i in range(4):
            s += chr(length / 256 ** i % 256 ** (i + 1))
        s += s
        s += '\xb1\x02\x00\x00' # 689
        s += data + '\x00'
        self.sendall(s)
    def pull(self):
        try: # for socket.settimeout
            return self.recv(9999)
        except Exception, e:
            return ''

class DouYuDanMuClient(AbstractDanMuClient):
    def _prepare_env(self):
        content = requests.get(self.url).content
        roomInfo = json.loads(re.search('\$ROOM = ({[\s\S]*?});', content).group(1))
        return ('openbarrage.douyutv.com', 8601), ('0.0.0.0', 80), roomInfo
    def _init_socket(self, danmu, heart, roomInfo):
        self.danmuSocket = _socket()
        self.danmuSocket.connect(danmu)
        self.danmuSocket.settimeout(3)
        self.danmuSocket.communicate('type@=loginreq/roomid@=%s/'%roomInfo['room_id'])
        self.danmuSocket.push('type@=joingroup/rid@=%s/gid@=-9999/'%roomInfo['room_id'])
    def _create_thread_fn(self, roomInfo):
        def keep_alive(self):
            self.danmuSocket.push('type@=keeplive/tick@=%s/'%int(time.time()))
            time.sleep(30)
        def get_danmu(self):
            if not select.select([self.danmuSocket], [], [], 1)[0]: return
            content = self.danmuSocket.pull()
            try:
                sender = [m.decode('utf8', 'ignore') for m in re.findall('/nn@=(.*?)/', content)]
                s = [m.decode('utf8', 'ignore') for m in re.findall('/txt@=(.*?)/', content)]
            except Exception, e:
                pass
            else:
                self.danmuWaitTime = time.time() + self.maxNoDanMuWait
                for m in zip(sender, s): self.msgPipe.append(m)
        return get_danmu, keep_alive # danmu, heart

if __name__ == '__main__':
    dc = DouYuDanMuClient('http://www.douyu.com/426530')
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
        print len(dc.msgPipe)
