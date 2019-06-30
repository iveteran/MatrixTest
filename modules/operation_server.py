# coding=utf-8

import asyncio
import functools
from modules.operation_protocol import OperationProtocol
from modules.operation_endpoint import OperationEndpoint
from modules.operation_commands import *

class OperationServer(object):
    def __init__(self, name, host, port, owner, loop):
        self.name = name
        self.host = host
        self.port = port
        self.owner = owner
        self.loop = loop
        self.command_map = {}
        self.endpoint_map = {}
        self.current_endpoint = None
        self.register_default_commands()
        self.server = None
        self.is_running = False

    def start_server(self):
        if not self.is_running:
            coro = self.loop.create_server(functools.partial(OperationProtocol, self), self.host, self.port)
            self.loop.create_task(coro)
            self.is_running = True
            print("Server %s running" % self.name)
        else:
            print("Server %s already in running" % self.name)

    def stop_server(self):
        print("Not implemented")
        #if self.server:
        #    self.server.close()
        #else:
        #    print("Operation server not created")

    def get_endpoint(self, name):
        return self.endpoint_map[name]

    def on_connection_made(self, protocol):
        print("opserver %s connection %s made" % (self.name, protocol.name))
        self.endpoint_map[protocol.name] = OperationEndpoint(self, protocol)

    def on_connection_lost(self, protocol):
        print("opserver %s connection %s lost" % (self.name, protocol.name))
        if protocol.name in self.endpoint_map:
            del self.endpoint_map[protocol.name]

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
            #self.owner.ui.execute(argv)
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

    def list_endpoint(self, pnum = 0):
        count = 0
        for name in self.endpoint_map:
            print(name)
            count += 1
            if pnum != 0 and count >= pnum:
                break
        print("total: %d, listed: %d" % (len(self.endpoint_map), count))

    def close_endpoint(self, name):
        if name in self.endpoint_map:
            self.endpoint_map[name].close()
            del self.endpoint_map[name]
        else:
            print("operation endpoint %s not exists" % name)

    def select(self, name = None):
        if not name:
            self.current_endpoint = None
            self.owner.ui.pop_operation()
        elif name in self.endpoint_map:
            self.current_endpoint = self.endpoint_map[name]
            self.owner.ui.push_operation(self.current_endpoint)
        else:
            print("[Error] Operation endpoint %s not exists" % name)

    def unselect(self):
        self.owner.select()

    def show_info(self):
        print("name: ", self.name)
        print("host: ", self.host)
        print("port: ", self.port)
        print("running: ", self.is_running)

    def register_default_commands(self):
        #self.register_command(OperationServerHelp(self))
        #self.register_command(OperationServerInfo(self))
        self.register_command(OperationHelp(self))
        self.register_command(OperationInfo(self))
        self.register_command(OperationServerRun(self))
        self.register_command(OperationServerStop(self))
        self.register_command(OperationListEndpoint(self))
        self.register_command(OperationSelectEndpoint(self))
        self.register_command(OperationCloseEndpoint(self))
