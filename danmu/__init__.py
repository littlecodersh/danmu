import re

from .DouYu import DouYuDanMuClient
from .Panda import PandaDanMuClient
from .ZhanQi import ZhanQiDanMuClient
from .QuanMin import QuanMinDanMuClient

__version__ = '1.0.0'
__all__     = ['DanMuClient']

def DanMuClient(url):
    for u in (('panda.tv', PandaDanMuClient),
            ('douyu.com', DouYuDanMuClient),
            ('quanmin.tv', QuanMinDanMuClient),
            ('zhanqi.tv', ZhanQiDanMuClient)):
        r = re.match('.*?%s/*.*?/[^/]*?$'%u[0], url)
        if r:
            if 'http://' == url[:7]: return u[1](url)
            return u[1]('http://' + url)
