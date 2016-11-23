# encoding: utf-8

import zmq
from configobj import ConfigObj


class Base(object):

    def __init__(self, logger, conf_path='config.ini'):
        self._conf = ConfigObj(conf_path)
        self._logger = logger
        self.debug = self._logger.debug
        self.info = self._logger.info
        self.error = self._logger.error
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

    def start(self):
        self.debug('Preparing')
        self.prepare()

        self.debug('Starting ... ')
        self._is_run = True
        while self._is_run:
            self.debug('Doing ...')
            self.do()
        self.debug('Done')

    def stop(self):
        self.debug('Stopping ...')
        self._is_run = False

        self.debug('Cleaning ... ')
        self.clean()


class WatcherBase(Base):
    pass


class ImporterBase(Base):
    pass
