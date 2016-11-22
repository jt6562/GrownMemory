#!/usr/bin/env python
# encoding: utf-8

import sys
print sys.path
print sys.argv


from configobj import ConfigObj

config = ConfigObj('config.ini')

print config

config['watchers']={'instance':['1,3']}

config.write()

print config
