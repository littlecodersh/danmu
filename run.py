import time

from danmu import DanMuClient

dc = DanMuClient('http://www.zhanqi.tv/huatuo')
dc.start()
while 1:
    if dc.msgPipe:
        print('[%s] %s' % dc.msgPipe.pop())
    else:
        time.sleep(.1)
