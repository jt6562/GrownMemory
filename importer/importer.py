# encoding: utf-8

import json
from multiprocessing import Process, Queue as mq
import multiprocessing
from threading import Thread
import zmq as zmq
import logging
import time
import common as BaseClasses

logger = logging.getLogger('main.importer.importer')


class Worker(object):

    def __init__(self, queue, exporter_sock, logger):
        self.queue = queue
        self.exporter_sock = exporter_sock
        self._logger = logger

    @classmethod
    def start(cls, queue, exporter_sock, logger):
        ins = cls(queue, exporter_sock, logger)
        ins.run()

    def process(self, job):
        pass

    def run(self):
        while 1:
            job = self.queue.get()
            logger.debug('get job %s %s ', job, self.exporter_sock.closed)
            self.process(job)
            if hasattr(self.queue, 'task_done'):
                self.queue.task_done()


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
            worker = Process(
                target=Worker.start,
                args=(self._queue, self.exporter_sock, self._logger))
            worker.start()
            self._workers.append(worker)

    def do(self):
        socks = dict(self._poller.poll())
        if self.watcher_sock in socks and socks[
                self.watcher_sock] == zmq.POLLIN:
            message = self.watcher_sock.recv_pyobj()
            self.debug("Recieved control command: %s" % message)
            self._queue.put(message)
            self.debug('Queue size: %d' % self._queue.qsize())

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
