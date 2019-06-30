#!/bin/env python3
# coding=utf-8

import optparse
import asyncio
import functools
import os
import signal
from modules.cui import *
from modules.opserver_factory import OpServerFactory

g_options = None

def shutdown(loop, signame):
   print("Got signal %s, Terminating..." % signame)
   loop.stop()

def handle_loop_exception(loop, context):
    print("Handle loop exception: ", context)

def main():
    loop = asyncio.get_event_loop()
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame), functools.partial(shutdown, loop, signame))
    
    loop.set_exception_handler(handle_loop_exception);

    cui = CUI(loop)

    opserver_factory = OpServerFactory(loop, cui)
    cui.set_operation_factory(opserver_factory)

    loop.run_forever()

if __name__ == '__main__':
    main()
