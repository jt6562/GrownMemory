# encoding: utf-8

from configobj import ConfigObj
import json
from multiprocessing import Process, JoinableQueue
import multiprocessing
from threading import Thread
import zmq
import logging

__logger = logging.getLogger('main.importer.importer')


class Worker(object):

    def __init__(self, queue, exporter_sock):
        self.queue = queue
        self.exporter_sock = exporter_sock

    @classmethod
    def start(cls, queue, exporter_sock):
        ins = cls(queue, exporter_sock)
        ins.run()

    def run(self):
        while 1:
            job = self.queue.get()
            print 'get job', job, multiprocessing.current_process().name
            self.queue.task_done()


class MainLoop(object):

    def __init__(self, logger, conf_path='config.ini'):
        self._conf = ConfigObj(conf_path)
        self.__logger = logger

        context = zmq.Context.instance()

        self.watcher_sock = context.socket(zmq.PULL)
        self.exporter_sock = context.socket(zmq.PUB)

        self.is_stop = False
        self.queue = JoinableQueue()
        self.workers = []

    @property
    def config(self):
        return self._conf

    def run(self):
        self.__logger.info('Starting Main loop')
        self.watcher_sock.bind("tcp://*:%s" %
                               self._conf['general']['watcher_port'])
        self.__logger.info('Listening watcher message, on port: %s' %
                           str(self.config['general']['watcher_port']))
        self.exporter_sock.bind("tcp://*:%s" %
                                self._conf['general']['exporter_port'])
        self.__logger.info('Listening exporter publisher, on port: %s' %
                           str(self.config['general']['watcher_port']))

        # self.__logger.addHandler(
        # zmq.log.handlers.PUBHandler(self.exporter_sock))

        poller = zmq.Poller()
        poller.register(self.watcher_sock, zmq.POLLIN)
        # poller.register(self.exporter_sock, zmq.POLLOUT)

        for i in range(int(self._conf['general']['importer_count'])):
            worker = Process(
                target=Worker.start, args=(self.queue, self.exporter_sock))
            worker.start()
            self.workers.append(worker)

        while not self.is_stop:
            socks = dict(poller.poll())
            if self.watcher_sock in socks and socks[
                    self.watcher_sock] == zmq.POLLIN:
                message = self.watcher_sock.recv_pyobj()
                self.__logger.debug("Recieved control command: %s" % message)
                self.queue.put(message)
                self.__logger.debug('Queue size: %d' % self.queue.qsize())

    def stop(self):
        self.is_stop = True
        self.queue.join()
        for i in range(self._conf['general']['importer_count']):
            self.workers[i].join()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    loop = MainLoop(__logger, 'config.ini')

    loop.run()
    # def s(l):
    #     print l
    #     l.run()
    #
    # Process(target=lambda l: l.run(), args=(loop,)).start()

    context = zmq.Context.instance()

    socket = context.socket(zmq.PUSH)
    print loop.config['general']['watcher_port']
    socket.connect("tcp://localhost:%s" %
                   loop.config['general']['watcher_port'])
    print 'connected'
    socket.send_pyobj(222222)
