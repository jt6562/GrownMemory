# encoding: utf-8

import os
import json
import hashlib
import exifread
from six import StringIO

import common as BaseClasses


class Worker(BaseClasses.Base):

    def __init__(self, logger, queue, exporter_sock):
        super(Worker, self).__init__(logger)
        self.queue = queue
        self.exporter_sock = exporter_sock
        self._logger = logger

    @classmethod
    def start(cls, queue, exporter_sock, logger):
        ins = cls(queue, exporter_sock, logger)
        ins.run()

    def _exif(self, file_type, file_content):
        if file_type == 'image':
            content_f = StringIO(file_content)
            extra_attrs = exifread.process_file(content_f, details=False)
            extra_attrs = {k: extra_attrs[k].printable for k in extra_attrs}

    def process(self, job):
        file_content = job['content']
        sha1 = hashlib.sha1(file_content).hexdigest()
        file_name, file_ext = os.path.splitext(job['name'])
        file_info = {
            'file_type': job['type'],
            'name': file_name,
            'file_ext': file_ext,
            'hash': sha1,
            'content': file_content
        }

        extra_attrs = None
        if job['type'] == 'image':
            extra_attrs = self._exif(job['type'], file_content)

        file_info.update({'extra': extra_attrs})
        self.debug("Process file:" + json.dumps(file_info, indent=4))

    def run(self):
        count = 1
        while 1:
            job = self.queue.get()
            self.debug('get job %s %s ', job['source'], job['name'])
            self.process(job)
            if hasattr(self.queue, 'task_done'):
                self.queue.task_done()
