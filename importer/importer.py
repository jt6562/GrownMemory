# encoding: utf-8

import json
import logging
import time
import multiprocessing
from multiprocessing import Process, Queue as mq
import zmq as zmq

import common as BaseClasses
import worker

logger = logging.getLogger('main.importer.importer')


class MainLoop(BaseClasses.ImporterBase):

    def __init__(self, *args, **kw):
        super(MainLoop, self).__init__(*args, **kw)
        self.watcher_sock = self.zmq_ctx.socket(zmq.PULL)
        self.exporter_sock = self.zmq_ctx.socket(zmq.PUB)

        self.is_stop = False
        self._queue = mq()
        self._workers = []

    def prepare(self):
        self.info('Starting Main loop')
        self.watcher_sock.bind("tcp://*:%s" %
                               self.config['general']['watcher_port'])
        self.info('Listening watcher message, on port: %s' %
                  str(self.config['general']['watcher_port']))
        self.exporter_sock.bind("tcp://*:%s" %
                                self.config['general']['exporter_port'])
        self.info('Listening exporter publisher, on port: %s' %
                  str(self.config['general']['watcher_port']))

        poller = zmq.Poller()
        poller.register(self.watcher_sock, zmq.POLLIN)
        # poller.register(self.exporter_sock, zmq.POLLOUT)
        self._poller = poller

        for i in range(int(self.config['general']['importer_count'])):
            worker_instance = Process(
                target=worker.Worker.start,
                args=(self._logger, self._queue, self.exporter_sock))
            worker_instance.start()

            self._workers.append(worker_instance)

    def do(self):
        socks = dict(self._poller.poll())
        if self.watcher_sock in socks and socks[
                self.watcher_sock] == zmq.POLLIN:
            message = self.watcher_sock.recv_pyobj()
            if not message or 'content' not in message or not message[
                    'content']:
                return

            self.debug("Recieved event: %s" % message['type'])
            self._queue.put(message)

    def clean(self):
        self._queue.join()
        for i in range(self._conf['general']['importer_count']):
            self.workers[i].join()

        self.watcher_sock.disconnect()
        self.exporter_sock.disconnect()


def main():
    loop = MainLoop(logger, 'config.ini')
    loop.start()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
