# coding=utf-8

import functools
from modules.operation_protocol import OperationProtocol
from modules.operation_endpoint import OperationEndpoint
from modules.operation_commands import *

class OperationClient(object):
    def __init__(self, name, host, port, owner, loop):
        self.name = name
        self.host = host
        self.port = port
        self.owner = owner
        self.loop = loop
        self.endpoint = None
        self.command_map = {}
        self.register_default_commands()

    def start_client(self):
        coro = self.loop.create_connection(functools.partial(OperationProtocol, self, True), self.host, self.port)
        self.loop.create_task(coro)

    def stop_client(self):
        if self.endpoint:
            self.endpoint.close()
            self.endpoint = None
        else:
            print("Operation client has no connection")

    def get_endpoint(self):
        return self.endpoint

    def on_connection_made(self, protocol):
        print("opserver %s connection %s made" % (self.name, protocol.name))
        self.endpoint = OperationEndpoint(self, protocol)

    def on_connection_lost(self, protocol):
        print("opclient %s connection %s lost" % (self.name, protocol.name))
        self.endpoint = None

    def register_command(self, cmd):
        self.command_map[cmd.name] = cmd
        for alias in cmd.aliases:
            self.command_map[alias] = cmd

    def execute(self, argv):
        if len(argv) == 0: return

        success = False
        cmd = argv[0].strip()
        params = argv[1:] if len(argv) > 1 else []
        if cmd[0] == '.':
            params.insert(0, cmd[1:])
            success = self.owner.execute(params)
        elif cmd in self.command_map:
            success = self.command_map[cmd].execute(params)
        else:
            print('Unknown command: %s' % cmd)
        return success

    def show_usage(self, cmd = None):
        if cmd:
            self.show_cmd_usage(cmd)
        else:
            self.list_all_cmd_usage()

    def show_cmd_usage(self, cmd):
        if cmd in self.command_map:
            self.command_map[cmd].show_usage()
        else:
            print('Unknown command: %s' % cmd)

    def list_all_cmd_usage(self):
        for cmd_name, cmd in self.command_map.items():
            if not cmd.is_alias_cmd(cmd_name):
                cmd.show_usage()

    def show_info(self):
        print("name: ", self.name)
        print("host: ", self.host)
        print("port: ", self.port)
        print("endpoint: ", self.endpoint.name if self.endpoint else '')

    def register_default_commands(self):
        self.register_command(OperationHelp(self))
        self.register_command(OperationInfo(self))
        self.register_command(OperationClientRun(self))
        self.register_command(OperationClientStop(self))
