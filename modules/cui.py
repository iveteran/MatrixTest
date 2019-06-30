# coding=utf-8

import sys
import asyncio
from modules.operation_base import Command

class CUI(object):
    def __init__(self, loop):
        self.loop = loop
        self.op_stack = []
        self.command_map = {}
        self.register_default_commands()
        #self.loop.add_reader(sys.stdin.fileno(), self.repl)
        self.loop.create_task(self.repl_2())
        print('> Type \'help\' to get help', flush=True)

    def set_operation_factory(self, operation_factory):
        self.operation_factory = operation_factory

    def get_current_operation(self):
        #return self.operation_factory.get_current_operation() if self.operation_factory else None
        return self.op_stack[-1] if len(self.op_stack) > 0 else None

    def get_parent_operation(self):
        #return self.operation_factory.get_current_operation() if self.operation_factory else None
        return self.op_stack[-2] if len(self.op_stack) > 1 else self

    def push_operation(self, operation):
        self.op_stack.append(operation)

    def pop_operation(self):
        if len(self.op_stack) > 0:
            self.op_stack.pop()

    def get_prompt(self):
        return '/'.join([item.name for item in self.op_stack]) + '> '

    def repl(self):
        #print('> ', end='', flush=True)
        #user_input = sys.stdin.readline()
        user_input = input(self.get_prompt()) 
        cmd_argv = user_input.split()
        try:
            cmd = self.handle_command(cmd_argv)
            if not self.is_quit_command(cmd):
                self.repl()
        except Exception as err:
            print("Error: ", err)
            sys.exit(1)

    @asyncio.coroutine
    def repl_2(self):
        print(self.get_prompt(), end='', flush=True)
        user_input = yield from self.loop.run_in_executor(None, sys.stdin.readline)
        cmd_argv = user_input.split()
        cmd, success = self.handle_command(cmd_argv)
        #print("REPL: cmd: %s, success: %s" % (cmd, success))
        if not success or not self.is_quit_command(cmd):
            yield from self.repl_2()
        elif success:
            print('Exit REPL (cmd: %s)' % cmd)

    def register_command(self, cmd_obj):
        self.command_map[cmd_obj.name] = cmd_obj
        for cmd_alias in cmd_obj.aliases:
            self.command_map[cmd_alias] = cmd_obj

    def handle_command(self, argv):
        if len(argv) == 0: return None, None
        cmd = argv[0]
        success = False
        if self.get_current_operation():
            success = self.get_current_operation().execute(argv)
        else:
            success = self.execute(argv)
        return cmd, success

    def execute(self, argv):
        cmd = argv[0]
        success = False
        if cmd in self.command_map:
            success = self.command_map[cmd].execute(argv[1:])
        else:
            print("Unknown command: %s" % cmd)
        return success

    def show_usage(self, params):
        if len(params) == 0:
            self.show_all_cmd_usage()
        else:
            cmd = params[0]
            if cmd in self.command_map:
                self.command_map[cmd].show_usage()
            else:
                print("Unknown command: %s" % cmd)

    def show_all_cmd_usage(self):
        for cmd in self.command_map.keys():
            cmd_obj = self.command_map[cmd]
            if not cmd_obj.is_alias_cmd(cmd):
                cmd_obj.show_usage()

    def is_quit_command(self, cmd):
        return cmd == 'quit' or cmd in self.command_map['quit'].aliases

    def register_default_commands(self):
        self.register_command(CUICommandExit(self))
        self.register_command(CUICommandHelp(self))

class CUICommand(Command):
    def __init__(self, name, owner):
        super().__init__(name, owner)

class CUICommandExit(CUICommand):
    def __init__(self, owner):
        super().__init__("quit", owner)
        self.aliases = ['q', 'exit']

    def execute(self, argv):
        self.owner.loop.stop()
        return True

    def show_usage(self):
        print("quit | exit")

class CUICommandHelp(CUICommand):
    def __init__(self, owner):
        super().__init__("help", owner)
        self.aliases = ['?']

    def execute(self, argv):
        self.owner.show_usage(argv)
        return True

    def show_usage(self):
        print("help | ? [command]")
