# encoding: utf-8

import logging
import zmq
import common as BaseClasses

logger = logging.getLogger('main.exporters.base')


class Exporter(BaseClasses.ExporterBase):

    def __init__(self, *args, **kw):
        super(Exporter, self).__init__(*args, **kw)
        self.exporter_sock = self.zmq_ctx.socket(zmq.SUB)

    def __del__(self):
        self.exporter_sock.close()

    def prepare(self):
        dest = 'tcp://localhost:%s' % self.config['general']['exporter_port']
        logger.info('Connecting %s', dest)
        self.exporter_sock.connect(dest)
        logger.info('Subscribing all message')
        self.exporter_sock.setsockopt(zmq.SUBSCRIBE, '')

    def recv(self):
        return self.exporter_sock.recv_pyobj()

    def clean(self):
        self.exporter_sock.disconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    exporter = Exporter('config.ini')
    exporter.start()
