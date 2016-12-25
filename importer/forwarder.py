# encoding: utf-8

import json
import logging
import time
# import zmq.green as zmq
import zmq
import time

import common as BaseClasses
import worker

logger = logging.getLogger('main.importer.forwarder')


class Forwarder(BaseClasses.Service):

    def __init__(self, *args, **kw):
        super(Forwarder, self).__init__(*args, **kw)

        self.is_stop = False

    def prepare(self):
        pass

    def run(self):
        self.forwarder_insock = self.zmq_ctx.socket(zmq.SUB)
        self.forwarder_insock.bind("tcp://*:%s" %
                                   self.config['general']['forwarder_inport'])
        self.forwarder_insock.setsockopt(zmq.SUBSCRIBE, "")
        logger.info('Listening worker connect, on port: %s' %
                    str(self.config['general']['forwarder_inport']))

        self.forwarder_outsock = self.zmq_ctx.socket(zmq.PUB)
        self.forwarder_outsock.bind("tcp://*:%s" %
                                    self.config['general']['forwarder_outport'])
        logger.info('Listening exporter connect, on port: %s' %
                    str(self.config['general']['forwarder_outport']))

        logger.info('Starting job forwarder')
        zmq.device(zmq.FORWARDER, self.forwarder_insock, self.forwarder_outsock)

    def clean(self):
        self.forwarder_insock.disconnect()
        self.forwarder_outsock.disconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    forwarder = Forwarder('config.ini')
    forwarder.start()
