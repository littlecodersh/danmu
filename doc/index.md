# danmu

danmu 是一个开源的直播平台弹幕接口，使用他没什么基础的你也可以轻松的操作各平台弹幕。

使用不到三十行代码，你就可以使用Python基于弹幕进一步开发。

支持斗鱼、熊猫、战旗、全民、Bilibili多平台弹幕。

支持各版本Python，无平台依赖，方便各类开发者、爱好者使用。

一次开启，主播上线自动连接，下线后上线自动重连。

经过深度优化，几乎不漏过任何一条弹幕；使用抽象构架，方便修改与开发。

## Documents

你可以在[这里][document]获取使用帮助。

## Installation

可以通过本命令安装 danmu：

```bash
pip install danmu
```

## Simple uses

通过如下代码，可以初步通过Python对弹幕进行处理。

```python
import time, sys

from danmu import DanMuClient

def pp(msg):
    print(msg.encode(sys.stdin.encoding, 'ignore').
        decode(sys.stdin.encoding))

dmc = DanMuClient('http://www.douyu.com/lslalala')
if not dmc.isValid(): print('Url not valid')

@dmc.danmu
def danmu_fn(msg):
    pp('[%s] %s' % (msg['NickName'], msg['Content']))

@dmc.gift
def gift_fn(msg):
    pp('[%s] sent a gift!' % msg['NickName'])

@dmc.other
def other_fn(msg):
    pp('Other message received')

dmc.start(blockThread = True)
```

## Screenshot

![screenshot][screenshot]

## Advanced uses

### 设置默认的消息处理方式

消息被分为三种类型注册：danmu, gift, other

分别对应：普通弹幕，礼物消息，其他消息

如果某种类型没有注册过，将会使用默认方法，默认方法的注册方式如下：

```python
from danmu import DanMuClient

dmc = DanMuClient('http://www.douyu.com/lslalala')

@dmc.default
def default_fn(msg):
    pp('[%s] %s' % (msg['NickName'], msg['Content']))
```

### 取消已经注册过的方法

通过以下方式可以取消某一种类型的注册。

```python
from danmu import DanMuClient

dmc = DanMuClient('http://www.douyu.com/lslalala')
dmc.default(None)
dmc.gift(None)
```

## FAQ

Q: 获取的消息格式都是什么？

A: 消息为一个字典，必有三个键：NickName、Content、MsgType，对应用户名、消息内容、消息类型。

## Comments

如果有什么问题或者建议都可以在这个[Issue][issue#2]和我讨论

或者也可以在gitter上交流：[![gitter][gitter_picture]][gitter]

[py2]: https://img.shields.io/badge/python-2.7-ff69b4.svg "python2"
[py3]: https://img.shields.io/badge/python-3.5-red.svg "python3"
[english_version]: https://github.com/littlecodersh/danmu/blob/master/README_EN.md
[document]: http://danmu.readthedocs.io/zh_CN/latest/
[screenshot]: http://7xrip4.com1.z0.glb.clouddn.com/danmu/demo.png?imageView/2/w/400/ "screenshot"
[issue#2]: https://github.com/littlecodersh/danmu/issues/2
[gitter_picture]: https://badges.gitter.im/littlecodersh/danmu.svg "gitter"
[gitter]: https://gitter.im/littlecodersh/danmu?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge
