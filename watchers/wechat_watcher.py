#!/usr/bin/env python
# encoding: utf-8

from watchers import base
import gevent_inotifyx as inotify
import os
import logging
import json
import weixin
import gevent.monkey
import gevent.queue
gevent.monkey.patch_all()

logger = logging.getLogger('main.watchers.wechat')


class MyWeChat(weixin.WebWeixin):

    def __init__(self, queue, contacts):
        super(MyWeChat, self).__init__()
        self.queue = queue
        self.contacts = contacts

    def handleMsg(self, messages):
        # super(MyWeChat, self).handleMsg(message)
        for msg in messages['AddMsgList']:
            msg_type = msg['MsgType']
            name = msg['FromUserName']
            msgid = msg['MsgId']

            content = None
            content_type = None
            file_ext = ''
            if msg_type == 3:
                content = self.webwxgetmsgimg(msgid)
                content_type = 'image'
                file_ext = '.jpg'
            elif msg_type == 62:
                content = self.webwxgetvideo(msgid)
                content_type = 'video'
                file_ext = '.mp4'
            else:
                logger.debug('Get a message: %s' % json.dumps(msg, indent=3))

            if content:
                self.queue.put({'content': content,
                                'type': content_type,
                                'name': msgid + file_ext})

    def webwxgetmsgimg(self, msgid):
        url = self.base_uri + \
            '/webwxgetmsgimg?MsgID=%s&skey=%s' % (msgid, self.skey)
        data = self._get(url)
        if data == '':
            data = None

        return data

    # Not work now for weixin haven't support this API
    def webwxgetvideo(self, msgid):
        url = self.base_uri + \
            '/webwxgetvideo?msgid=%s&skey=%s' % (msgid, self.skey)
        data = self._get(url, api='webwxgetvideo')
        if data == '':
            data = None

        return data


class WechatWatcher(base.Watcher):

    def __init__(self, watcher_name, *args, **kw):
        super(WechatWatcher, self).__init__(*args, **kw)
        self.contacts = self.config[watcher_name]['contacts']
        self.queue = gevent.queue.Queue()
        self.wechat = MyWeChat(self.queue, self.contacts)

    def prepare(self):
        super(WechatWatcher, self).prepare()

        # Login web wechat
        self.wechat.getUUID()
        self.wechat.genQRCode()
        self.wechat.waitForLogin()
        self.wechat.waitForLogin(0)
        self.wechat.login()
        self.wechat.webwxinit()
        self.wechat.webwxstatusnotify()
        self.wechat.webwxgetcontact()
        self.wechat.webwxbatchgetcontact()
        # self.wechat.listenMsgMode()
        gevent.spawn(self.wechat.listenMsgMode)

    def do(self):
        msg = self.queue.get()
        job = {'source': 'wechat'}
        job.update(msg)
        self.send(job)
        job.pop('content')
        self.info("Send a job: %s" % json.dumps(job, intent=4))

    def clean(self):
        super(WechatWatcher, self).clean()
        inotify.rm_watch(self._inotify_fd, self._wd)
        os.close(self._wd)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    watcher = WechatWatcher('wechat', logger, 'config.ini')
    watcher.start()
