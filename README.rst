danmu
=====

|py2| |py3| `Chinese Version <chinese_version_>`_

danmu is Chinese translation of chat message.

It is an open source chat message api for live platforms like douyu, panda, huya, zhanqi.

Using this, even without programming basis, you will have an easy access to chat messages.

With less than 30 lines of code, you may develop further with chat messages.

Douyu, panda, Zhanqi, Quanmin, bilibili are all supported.

It supports multi versions of python and platforms, making it available for all developers and amateurs.

Once started, it will auto connect when anchor showed up and re-connect when anchor connect again.

With good optimization and abstract structure, almost all chat messages will be catched and the whole program is easy to be modified.

Documents
>>>>>>>>>

You may find document `here <document_>`_.

Installation
>>>>>>>>>>>>

You may use this script to install danmu:

.. code:: bash

    pip install danmu

Simple uses
>>>>>>>>>>>

The following is a simple demo of how to use danmu.

.. code:: python

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

Advanced uses
>>>>>>>>>>>>>

**Set default chat message dealer**

Messages are split into three types to be registered: danmu, gift, other.

Which means: ordinary chat messages, gift messages, other messages.

.. code:: python

    from danmu import DanMuClient

    dmc = DanMuClient('http://www.douyu.com/lslalala')

    @dmc.default
    def default_fn(msg):
        pp('[%s] %s' % (msg['NickName'], msg['Content']))

**Cancel message dealer registered**

Using the following codes, you can cancel a message dealer registered.

.. code:: python

    from danmu import DanMuClient

    dmc = DanMuClient('http://www.douyu.com/lslalala')
    dmc.default(None)
    dmc.gift(None)

FAQ
>>>

Q: What's the message type of chat messages?

A: A dictionary with at least three keys, NickName, Content, MsgType.

Comments
>>>>>>>>

If you have any problem or suggestion, feel free to contact me through this `Issue <issue#2_>`_.

Or through gitter: |gitter|_

.. |py2| image:: https://img.shields.io/badge/python-2.7-ff69b4.svg
.. |py3| image:: https://img.shields.io/badge/python-3.5-red.svg
.. _chinese_version: https://github.com/littlecodersh/danmu/blob/master/README.md
.. _document: https://danmu.readthedocs.org/zh/latest/
.. |screenshot| image:: http://7xrip4.com1.z0.glb.clouddn.com/danmu/demo.png?imageView/2/w/400/
.. _issue#2: https://github.com/littlecodersh/danmu/issues/2
.. |gitter| image:: https://badges.gitter.im/littlecodersh/danmu.svg
.. _gitter: https://gitter.im/littlecodersh/danmu?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge
