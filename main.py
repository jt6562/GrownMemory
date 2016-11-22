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

import configobj
