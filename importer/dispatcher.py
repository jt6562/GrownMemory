# encoding: utf-8

import json
import logging
import time
import multiprocessing
from multiprocessing import Process, Queue as mq
# import zmq.green as zmq
import zmq
from zmq.devices import ProcessDevice, ThreadDevice
import time

import common as BaseClasses
import worker

logger = logging.getLogger('main.importer.dispatcher')


class Dispatcher(BaseClasses.Service):

    def __init__(self, *args, **kw):
        super(Dispatcher, self).__init__(*args, **kw)

        self.is_stop = False
        # self._queue = mq()
        # self._workers = []

    def prepare(self):
        pass

    def run(self):
        self.dispatcher_insock = self.zmq_ctx.socket(zmq.PULL)
        self.dispatcher_insock.bind("tcp://*:%s" %
                                    self.config['general']['dispatcher_inport'])
        logger.info('Listening watcher message, on port: %s' %
                    str(self.config['general']['dispatcher_inport']))

        self.dispatcher_outsock = self.zmq_ctx.socket(zmq.PUSH)
        self.dispatcher_outsock.bind(
            "tcp://*:%s" % self.config['general']['dispatcher_outport'])
        logger.info('Listening worker connect, on port: %s' %
                    str(self.config['general']['dispatcher_outport']))

        logger.info('Starting job dispatcher')
        zmq.device(zmq.STREAMER, self.dispatcher_insock,
                   self.dispatcher_outsock)

        # queue_device = ProcessDevice(zmq.FORWARDER, zmq.SUB, zmq.PUB)
        # queue_device.bind_in("tcp://*:%s" %
        #                      self.config['general']['device_inport'])
        # queue_device.setsockopt_in(zmq.SUBSCRIBE, "")
        # queue_device.bind_out("tcp://*:%s" %
        #                       self.config['general']['exporter_port'])
        # queue_device.start()
        # self.queue_device = queue_device

        # poller = zmq.Poller()
        # poller.register(self.watcher_sock, zmq.POLLIN)
        # # poller.register(self.exporter_sock, zmq.POLLOUT)
        # self._poller = poller
        #
        # for i in range(int(self.config['general']['importer_count'])):
        #     worker_instance = worker.Worker(
        #         self._queue, self.config['general']['device_inport'])
        #     worker_instance.start()
        #
        #     self._workers.append(worker_instance)

    # def do(self):
    #     socks = dict(self._poller.poll())
    #     if self.watcher_sock in socks and socks[
    #             self.watcher_sock] == zmq.POLLIN:
    #         message = self.watcher_sock.recv_pyobj()
    #         if not message or 'content' not in message or not message[
    #                 'content']:
    #             return
    #
    #         logger.debug("Recieved event: %s" % message['type'])
    #         self._queue.put(message)

    def clean(self):
        self.dispatcher_insock.disconnect()
        self.dispatcher_outsock.disconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    dispatcher = Dispatcher('config.ini')
    dispatcher.start()
