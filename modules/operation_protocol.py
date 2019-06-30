# coding=utf-8

import asyncio
from modules.message_protocol import MQ

class OperationProtocol(asyncio.Protocol):
    def __init__(self, creator, active = False):
        self.creator = creator
        self.active = active
        self.mq = MQ(self.handle_message)
        self.transport = None
        self.name = None
        self.localaddr = None
        self.peeraddr = None

    def connection_made(self, transport):
        self.transport = transport
        peeraddr = self.transport.get_extra_info('peername')
        self.peeraddr = '{}:{}'.format(peeraddr[0], peeraddr[1])
        localaddr = self.transport.get_extra_info('sockname')
        self.localaddr = '{}:{}'.format(localaddr[0], localaddr[1])
        self.name = self.localaddr if self.active else self.peeraddr
        print('[OperationProtocol] connection made: {}-{}'.format(self.localaddr, self.peeraddr))
        self.creator.on_connection_made(self)

    def data_received(self, data):
        self.mq.AppendData(data)

    def connection_lost(self, exception):
        self.creator.on_connection_lost(self)

    def handle_message(self, msg):
        self.creator.on_response_message(self, msg)

    def send_message(self, msg):
        self.transport.write(msg)

    def close(self):
        self.transport.close()

    def is_closing(self):
        return self.transport.is_closing()
