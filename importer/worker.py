# encoding: utf-8

import os
import json
import hashlib
# import exifread
import piexif
from piexif import ImageIFD, GPSIFD, ExifIFD
from six import StringIO
from multiprocessing import Process
import common as BaseClasses
import db
from datetime import datetime


class Worker(BaseClasses.Base, Process):

    def __init__(self, logger, queue, exporter_sock):
        Process.__init__(self)
        BaseClasses.Base.__init__(self, logger)
        self.queue = queue
        self.exporter_sock = exporter_sock
        self._logger = logger

    def _get_exif_by_piexif(self, file_content):
        _attrs = piexif.load(file_content)
        _need_attr = [
            ('width', 'Exif', ExifIFD.PixelXDimension, None),
            ('height', 'Exif', ExifIFD.PixelYDimension, None),
            ('ctime', 'Exif', ExifIFD.DateTimeOriginal,
             lambda s: datetime.strptime(s, "%Y:%m:%d %H:%M:%S")),
            ('orientation', '0th', ImageIFD.Orientation, None),
            ('make', '0th', ImageIFD.Make, None),
            ('model', '0th', ImageIFD.Model, None),
        ]

        exif = {}
        for attr in _need_attr:
            _tmp = _attrs.get(attr[1], None)
            if not _tmp:
                continue

            _tmp = _tmp.get(attr[2], None)
            if not _tmp:
                _tmp = None
            if _tmp and attr[3]:
                _tmp = attr[3](_tmp)

            exif.update({attr[0]: _tmp})

        # Compute image hash
        exif['img_eigen'] = ''

        return exif

    def get_exif(self, file_type, file_content):
        if file_type == 'image':
            exif = self._get_exif_by_piexif(file_content)

        return exif

    def _db_create_item(self, file_info):
        # TODO: Together all db operation into a class
        item, created = db.Photo.get_or_create(hash=file_info['hash'])
        return item, created

    def _db_update_state(self, item, new_state):
        item.state = new_state
        item.save()

    def _db_save_item(self, item, file_info):
        for k in file_info:
            if hasattr(item, k):
                setattr(item, k, file_info[k])
        item.save()

    def _db_save_item_to_conflict_photos(self, file_info):
        pass

    def send_to_exporter(self, file_info):
        # TODO, Send to exporter
        pass

    def process(self, job):

        file_content = job['content']
        sha_hash = hashlib.sha1(file_content).hexdigest()
        file_name, file_ext = os.path.splitext(job['filename'])
        file_info = {
            'file_type': job['type'],
            'file_orgin_name': file_name,
            'file_ext': file_ext.lower(),
            'file_hash': sha_hash,
            'itime': datetime.utcnow()
        }

        # Step 1
        # Step 2
        _new, _is_new = self._db_create_item(file_info)
        if not _is_new:
            self._db_save_item_to_conflict_photos(file_info)

        # Step 3
        self._db_update_state(_new, db.PhotoProcessState.parsing)
        exif = {}
        if job['type'] == 'image':
            exif = self.get_exif(job['type'], file_content)
        if not exif['ctime']:
            exif['ctime'] = job['ctime']

        file_info.update(exif)

        self.debug("Process file:" + json.dumps(
            file_info, cls=db.ItemJSONEncoder, ensure_ascii=False, indent=4))
        self._db_update_state(_new, db.PhotoProcessState.parsed)

        # Step 4
        self._db_save_item(_new, file_info)

        # Step 5
        self._db_update_state(_new, db.PhotoProcessState.outputting)
        file_info.update({'content': file_content})
        self.send_to_exporter(file_info)
        self._db_update_state(_new, db.PhotoProcessState.outputted)

    def run(self):
        count = 1
        while 1:
            job = self.queue.get()
            self.debug('get job %s %s ', job['source'], job['filename'])
            self.process(job)
            if hasattr(self.queue, 'task_done'):
                self.queue.task_done()
