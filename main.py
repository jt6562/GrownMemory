#!/usr/bin/env python
# encoding: utf-8
'''
Start all services as follow order

1. start web
2. start exporters
3. start importers
4. start watchers

The file `config.ini` define service count, listen port, and so on.
'''

from multiprocessing import Process
from configobj import ConfigObj
import sys
import logging
import importer
import watchers
import exporters

submodule = {
    'filewatcher': watchers.FileWatcher,
    'wechatwatcher': watchers.WechatWatcher,
    'direxporter': exporters.DirectoryExporter,
    'qnapexporter': None
}


def main(conf_path):
    conf = ConfigObj(conf_path)
    watchers = conf['general']['watchers']
    exporters = conf['general']['exporters']

    p_list = []
    importer_main = importer.MainLoop(conf_path)
    p = Process(target=importer_main.start)
    p.start()
    p_list.append(p)

    for sub_name in watchers + exporters:
        w_type = conf[sub_name]['type']
        sub = submodule[w_type.lower()](sub_name, conf_path)
        p = Process(target=sub.start)
        p.start()
        p_list.append(p)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    conf_path = sys.argv[1]
    main(conf_path)
