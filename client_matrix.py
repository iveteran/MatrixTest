#!/bin/env python3
# coding=utf-8

import optparse
import asyncio
import functools
import os
import signal
from modules.cui import *
from modules.opclient_factory import OpClientFactory

from modules.message_protocol import BinaryMessage
from modules.operation_echo import OperationEcho
from modules.operation_ping import OperationPing

#from modules.operation_client import OperationProtocol

g_options = None

def parse_args():
    usage = """usage: %prog [options] [host]:port"""

    parser = optparse.OptionParser(usage)

    global g_options
    g_options, args = parser.parse_args()
    print("options: %s" % g_options)

    if len(args) == 0:
        parser.error(usage)

    def parse_address(addr):
        if ':' not in addr:
            host = '0.0.0.0'
            port = addr
        else:
            host, port = addr.split(':', 1)

        if not port.isdigit():
            parser.error('Ports must be integers.')

        return host, int(port)

    return parse_address(args[0]) + (parse_address(args[1]) if (len(args) > 1) else ('', 0))


def shutdown(loop, signame):
   print("Got signal %s, Terminating..." % signame)
   loop.stop()

def handle_loop_exception(loop, context):
    print("Handle loop exception: ", context)

def main():
    #host, port = parse_args()
    host, port =  "127.0.0.1", 8888

    loop = asyncio.get_event_loop()
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame), functools.partial(shutdown, loop, signame))
    
    #loop.set_exception_handler(handle_loop_exception);

    cui = CUI(loop)

    opclient_factory = OpClientFactory(loop, cui, host, port)
    op_echo = OperationEcho(opclient_factory, BinaryMessage())
    opclient_factory.register_operation(op_echo)
    op_ping = OperationPing(opclient_factory, BinaryMessage())
    opclient_factory.register_operation(op_ping)

    cui.set_operation_factory(opclient_factory)

    loop.run_forever()

if __name__ == '__main__':
    main()
