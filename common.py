# encoding: utf-8

import zmq
from configobj import ConfigObj
import logging
from multiprocessing import Process

logger = logging.getLogger(__name__)


class Base(Process):
    pass


class Service(Base):

    def __init__(self, conf_path='config.ini'):
        super(Service, self).__init__()
        self._conf = ConfigObj(conf_path)
        self._zmq_ctx = zmq.Context()
        self._is_run = False

    def __del__(self):
        self._zmq_ctx.destroy()

    @property
    def zmq_ctx(self):
        return self._zmq_ctx

    @property
    def config(self):
        return self._conf

    @property
    def is_run(self):
        return self._is_run

    def prepare(self):
        raise NotImplementedError

    def do(self):
        """
        This function must block
        """
        raise NotImplementedError

    def clean():
        raise NotImplementedError

    def run(self):
        logger.debug('Preparing')
        self.prepare()

        logger.debug('Starting ... ')
        self._is_run = True
        while self._is_run:
            logger.debug('Waiting and do a job ...')
            self.do()
        logger.debug('Done')

    def stop(self):
        logger.debug('Stopping ...')
        self._is_run = False

        logger.debug('Cleaning ... ')
        self.clean()


class WatcherBase(Service):
    pass


class ImporterBase(Service):
    pass


class ExporterBase(Service):
    pass
