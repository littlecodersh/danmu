import re, threading, time, traceback

from .DouYu import DouYuDanMuClient
from .Panda import PandaDanMuClient
from .ZhanQi import ZhanQiDanMuClient
from .QuanMin import QuanMinDanMuClient
from .Bilibili import BilibiliDanMuClient

__version__ = '1.0.1'
__all__     = ['DanMuClient']

class DanMuClient(object):
    __url          = ''
    __baseClient   = None
    __client       = None
    __functionDict = {'default': lambda x: 0}
    __isRunning    = False
    def __init__(self, url):
        if 'http://' == url[:7]:
            self.__url = url
        else:
            self.__url = 'http://' + url
        for u, bc in {'panda.tv'    : PandaDanMuClient,
                'douyu.com'         : DouYuDanMuClient,
                'quanmin.tv'        : QuanMinDanMuClient,
                'zhanqi.tv'         : ZhanQiDanMuClient,
                'live.bilibili.com' : BilibiliDanMuClient, }.items() :
            if re.match(r'^(?:http://)?.*?%s/(.+?)$' % u, url):
                self.__baseClient = bc; break
    def __register(self, fn, msgType):
        if fn is None:
            if msgType == 'default':
                self.__functionDict['default'] = lambda x: 0
            elif self.__functionDict.get(msgType):
                del self.__functionDict[msgType]
        else:
            self.__functionDict[msgType] = fn
    def isValid(self):
        return self.__baseClient is not None
    def default(self, fn):
        self.__register(fn, 'default')
        return fn
    def danmu(self, fn):
        self.__register(fn, 'danmu')
        return fn
    def gift(self, fn):
        self.__register(fn, 'gift')
        return fn
    def other(self, fn):
        self.__register(fn, 'other')
        return fn
    def start(self, blockThread = False, pauseTime = .1):
        if not self.__baseClient or self.__isRunning: return False
        self.__client = self.__baseClient(self.__url)
        self.__client.start()
        self.__isRunning = True
        def _start():
            while self.__isRunning:
                if self.__client.msgPipe:
                    msg = self.__client.msgPipe.pop()
                    fn = self.__functionDict.get(msg['MsgType'],
                        self.__functionDict['default'])
                    try:
                        fn(msg)
                    except:
                        traceback.print_exc()
                else:
                    time.sleep(pauseTime)
        if blockThread:
            try:
                _start()
            except KeyboardInterrupt:
                print('Bye~')
        else:
            danmuThread = threading.Thread(target = _start)
            danmuThread.setDaemon(True)
            danmuThread.start()
        return True
    def stop(self):
        self.__isRunning = False
        if self.__client: self.__client.deprecated = True
