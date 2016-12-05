# encoding: utf-8

import logging
import zmq
import common as BaseClasses

logger = logging.getLogger('main.watchers.base')


class Watcher(BaseClasses.WatcherBase):

    def __init__(self, *args, **kw):
        super(Watcher, self).__init__(*args, **kw)
        self.watcher_sock = self.zmq_ctx.socket(zmq.PUSH)

    def __del__(self):
        self.watcher_sock.close()

    def prepare(self):
        dest = 'tcp://localhost:%s' % self.config['general']['watcher_port']
        logger.info('Connecting %s', dest)
        self.watcher_sock.connect(dest)

    def send(self, job):
        self.watcher_sock.send_pyobj(job)

    def clean(self):
        self.watcher_sock.disconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    watcher = Watcher('config.ini')
    watcher.start()
