#!/usr/bin/env python
# encoding: utf-8

import zmq

context = zmq.Context.instance()

socket = context.socket(zmq.PUSH)
socket.connect("tcp://localhost:5556")
print 'connected'
socket.send_pyobj(222222)
