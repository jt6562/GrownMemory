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
import os
import argparse
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


def start_service(service, instance_name, conf_path):
    services_list = []
    for instance in instance_name:
        service = service(instance, conf_path)
        service.start()
        services_list.append(service)

    [service.join() for service in services_list if hasattr(service, 'join')]


def start_importer(conf_path):
    importer_main = importer.MainLoop(conf_path)
    importer_main.start()


def start_file_watchers(conf_path):
    conf = ConfigObj(conf_path)
    file_watchers = conf['general']['file_watchers']
    return start_service(watchers.FileWatcher, file_watchers, conf_path)


def start_wechat_watcher(conf_path):
    conf = ConfigObj(conf_path)
    wechat_watcher = conf['general']['wechat_watcher']
    return start_service(watchers.FileWatcher, [wechat_watcher], conf_path)


def start_dir_exporter(conf_path):
    conf = ConfigObj(conf_path)
    dir_exporter = conf['general']['dir_exporter']
    return start_service(exporters.DirectoryExporter, [dir_exporter], conf_path)


def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument(
        'service',
        choices=[
            'file_watchers', 'wechat_watcher', 'importer', 'dir_exporter',
            'qnap_exporter'
        ],
        help='file_watchers|wechat_watcher|importer|dir_exporter|qnap_exporter')
    parser.add_argument("-c", help="configuration file", action="store")
    parser.add_argument(
        "-v", help="increase output verbose", action="store_true")

    args = parser.parse_args()

    conf_path = os.path.abspath(args.c)
    print conf_path, 111

    level = logging.INFO
    if args.v:
        level = logging.DEBUG
    logging.basicConfig(level=level)

    if args.service == 'file_watchers':
        return start_file_watchers(conf_path)
    elif args.service == 'wechat_watcher':
        return start_wechat_watcher(conf_path)
    elif args.service == 'importer':
        return start_importer(conf_path)
    elif args.service == 'dir_exporter':
        return start_dir_exporter(conf_path)
    else:
        raise NotImplementedError


if __name__ == '__main__':
    main()
