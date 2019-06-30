# coding=utf-8

import functools
from modules.operation_commands import *

class OperationEndpoint(object):
    def __init__(self, owner, protocol):
        self.owner = owner
        self.name = protocol.name
        self.protocol = protocol
        self.command_map = {}
        self.operation_map = {}
        self.register_default_commands()

    def close(self):
        self.protocol.close()
        self.protocol = None

    def address_pair(self):
        return "{}-{}".format(self.protocol.localaddr, self.protocol.peeraddr)

    def on_response_message(self, msg):
        print("on_response_message")
        cmd = msg.cmd
        if cmd in self.operation_map:
            self.operation_map[cmd].handle_response(msg)
        else:
            print('Unknown response: %s' % cmd)

    def register_operation(self, operation):
        self.operation_map[operation.name] = operation
        for alias in operation.aliases:
            self.operation_map[alias] = operation

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
        elif cmd in self.operation_map:
            success = self.operation_map[cmd].execute(self.protocol, params)
        else:
            print('Unknown command: %s' % cmd)
        return success

    def unselect(self):
        self.owner.unselect()

    def show_usage(self, cmd = None):
        if cmd:
            self.show_cmd_usage(cmd)
        else:
            self.list_all_cmd_usage()

    def show_cmd_usage(self, cmd):
        if cmd in self.operation_map:
            self.operation_map[cmd].show_usage()
        else:
            print('Unknown command: %s' % cmd)

    def list_all_cmd_usage(self):
        for cmd_name, cmd in self.command_map.items():
            if not cmd.is_alias_cmd(cmd_name):
                cmd.show_usage()
        for op_name, op in self.operation_map.items():
            if not op.is_alias_cmd(op_name):
                op.show_usage()

    def show_info(self):
        print("name: ", self.protocol.name)
        print("address pair: ", self.address_pair())

    def register_default_commands(self):
        self.register_command(OperationHelp(self))
        self.register_command(OperationInfo(self))
        self.register_command(OperationEndpointUnselect(self))
