#!/usr/bin/env python
# encoding: utf-8

from exporters import base
import gevent_inotifyx as inotify
import os
import logging
from datetime import datetime
from time import mktime
import zmq
# import gevent.monkey
# gevent.monkey.patch_all()

logger = logging.getLogger('main.exporters.file')

import json
from database import ItemJSONEncoder


class DirectoryExporter(base.Exporter):

    def __init__(self, exporter_name, *args, **kw):
        super(DirectoryExporter, self).__init__(*args, **kw)
        self.export_path = self.config[exporter_name]['path']

    def prepare(self):
        super(DirectoryExporter, self).prepare()
        if not os.path.exists(self.export_path):
            os.mkdir(self.export_path)

        if not os.path.isdir(self.export_path):
            os.remove(self.export_path)
            os.mkdir(self.export_path)

        poller = zmq.Poller()
        poller.register(self.exporter_sock, zmq.POLLIN)
        self._poller = poller

    def do(self):
        socks = dict(self._poller.poll())
        if self.exporter_sock in socks and socks[
                self.exporter_sock] == zmq.POLLIN:
            job = self.recv()

            keys = [k for k in job]
            logger.debug("Recieved job: %s" % str(keys))
            file_content = job.pop('content', None)
            if not file_content:
                return
            logger.debug(json.dumps(job, cls=ItemJSONEncoder, indent=4))

            file_name = job['file_hash'] + job['file_ext']
            file_path = os.path.join(self.export_path, file_name)
            ctime = mktime(job['ctime'].timetuple())

            with open(file_path, 'w') as f:
                f.write(file_content)
                f.flush()

            os.utime(file_path, (ctime, ctime))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    exporter = DirectoryExporter('outdir', 'config.ini')
    exporter.start()
