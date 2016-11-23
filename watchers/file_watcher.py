#!/usr/bin/env python
# encoding: utf-8

from watchers import base
import gevent_inotifyx as inotify
import os
import logging
import gevent.monkey
gevent.monkey.patch_all()

logger = logging.getLogger('main.watchers.file')


class FileWatcher(base.Watcher):

    def __init__(self, watcher_name, *args, **kw):
        super(FileWatcher, self).__init__(*args, **kw)
        self.watch_path = self.config[watcher_name]['path']
        self._file_exts = self.config[watcher_name]['file_exts']

    def prepare(self):
        super(FileWatcher, self).prepare()
        self._inotify_fd = inotify.init()
        self._wd = inotify.add_watch(self._inotify_fd, self.watch_path,
                                     inotify.IN_CLOSE_WRITE)

    def do(self):
        events = inotify.get_events(self._inotify_fd)
        for ev in events:
            filename = os.path.join(self.watch_path, ev.name)
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext not in self._file_exts:
                self.debug('Invalid file[%s] extension[%s] %s' %
                           (filename, file_ext, self._file_exts))
                continue

            with open(filename, 'r') as f:
                job = {'source': filename, 'content': f.read()}
            self.info('Get a file: %s' % filename)
            self.send(job)
            os.remove(filename)

    def clean(self):
        super(FileWatcher, self).clean()
        inotify.rm_watch(self._inotify_fd, self._wd)
        os.close(self._wd)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    watcher = FileWatcher('indir1', logger, 'config.ini')
    watcher.start()
