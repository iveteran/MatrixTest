# coding=utf-8

from modules.cui import CUICommand
from modules.operation_server import OperationServer

class OpServerFactory(object):
    def __init__(self, loop, ui):
        self.loop = loop
        self.ui = ui
        self.opserver_map = {}
        self.current_opserver = None
        self.operation_list = []
        self.register_default_commands()

    def create_opserver(self, name, port, host = None):
        #name = (host or 'localhost') + ':' + str(port)
        if name in self.opserver_map:
            print("[Error] Operation server %s already exists" % name)
        else:
            opserver = OperationServer(name, host, port, self, self.loop)
            self.opserver_map[name] = opserver
            for operation in self.operation_list:
                opserver.register_operation(operation)

    def batch_create_opserver(self, begin_port, end_port, host = None):
        for port in range(begin_port, end_port):
            name = (host or 'localhost') + ':' + str(port)
            self.create_opserver(port, host)

    def drop_opserver(self, name):
        if self.current_opserver and name == self.current_opserver.name:
            print("[Error] Can not drop an opserver that in use currently")
        elif name in self.opserver_map:
            self.stop_opserver(name)
            del self.opserver_map[name]
        else:
            print("[Error] Operation server %s not exists" % name)

    def run_opserver(self, name):
        if name in self.opserver_map:
            self.opserver_map[name].start_server()
        else:
            print("[Error] Operation server %s not exists" % name)

    def run_all_opserver(self):
        for opserver in self.opserver_map.values():
            opserver.start_server()

    def stop_opserver(self, name = None):
        if name in self.opserver_map:
            self.opserver_map[name].stop_server()
        else:
            print("[Error] Operation server %s not exists" % name)

    def stop_all_opserver(self):
        for opserver in self.opserver_map.values():
            opserver.stop_server()

    def list_opserver2(self, pnum = 10):
        print("Operation servers[%d]: %s" % (len(self.opserver_map), self.opserver_map.keys()[:pnum]))

    def list_opserver(self, pnum = 0):
        count = 0
        for name in self.opserver_map:
            print(name)
            count += 1
            if pnum != 0 and count >= pnum:
                break
        print("total: %d, listed: %d" % (len(self.opserver_map), count))

    def select(self, name = None):
        if not name:
            self.current_opserver = None
            self.ui.pop_operation()
        elif name in self.opserver_map:
            self.current_opserver = self.opserver_map[name]
            self.ui.push_operation(self.current_opserver)
        else:
            print("[Error] Operation server %s not exists" % name)

    def execute(self, argv):
        self.ui.execute(argv)

    def show_info_opserver(self):
        for name in self.opserver_map:
            print("%s", name)
        print("select opserver: ", self.current_opserver.name if self.current_opserver else '')

    def get_current_opserver(self):
        return self.current_opserver

    def get_current_operation(self):
        return self.get_current_opserver()

    def register_operation(self, operation):
        self.operation_list.append(operation)

    def register_default_commands(self):
        self.ui.register_command(CUICommandCreateServer(self))
        self.ui.register_command(CUICommandBatchCreateServer(self))
        self.ui.register_command(CUICommandDropServer(self))
        self.ui.register_command(CUICommandSelectServer(self))
        self.ui.register_command(CUICommandListServer(self))
        self.ui.register_command(CUICommandRunServer(self))
        self.ui.register_command(CUICommandStopServer(self))
        self.ui.register_command(CUICommandRunAllServer(self))
        self.ui.register_command(CUICommandStopAllServer(self))
        self.ui.register_command(CUICommandInfoServer(self))

class CUICommandCreateServer(CUICommand):
    def __init__(self, owner):
        super().__init__("create", owner)

    def execute(self, argv):
        if self.validate_parameters(argv):
            name = argv[0]
            host, port = argv[1].split(':') if len(argv) >= 2 else [None, None]
            self.owner.create_opserver(name, port, host)
        else:
            self.show_usage()

    def validate_parameters(self, params):
        if len(params) == 2:
            host, port = params[1].split(':')
            return port.isdigit()
        else:
            return False

    def show_usage(self):
        print("%s <name> <host:port> - create operation server" % self.name)

class CUICommandBatchCreateServer(CUICommand):
    def __init__(self, owner):
        super().__init__("batch_create", owner)

    def execute(self, argv):
        if self.validate_parameters(argv):
            begin_port = int(argv[0])
            end_port = int(argv[1])
            host = int(argv[2]) if len(argv) >= 3 else None
            self.owner.batch_create_opserver(begin_port, end_port, host)
        else:
            self.show_usage()

    def validate_parameters(self, params):
        if len(params) == 3 and params[0].isdigit() and params[1].isdigit():
            return True
        else:
            return False

    def show_usage(self):
        print("%s <begin port> <end port> [host] - batch create operation server" % self.name)

class CUICommandSelectServer(CUICommand):
    def __init__(self, owner):
        super().__init__("select", owner)

    def execute(self, argv):
        opserver_name = argv[0] if len(argv) > 0 else None
        self.owner.select(opserver_name)

    def show_usage(self):
        print("%s [opserver] - select operation server" % self.name)

class CUICommandListServer(CUICommand):
    def __init__(self, owner):
        super().__init__("list", owner)

    def execute(self, argv):
        if self.validate_parameters(argv):
            pnum = int(argv[0]) if len(argv) > 0 else 20
            self.owner.list_opserver(pnum)
        else:
            self.show_usage()

    def validate_parameters(self, params):
        return len(params) == 0 or (len(params) == 1 and params[0].isdigit())

    def show_usage(self):
        print("%s [print num] - list operation server" % self.name)

class CUICommandDropServer(CUICommand):
    def __init__(self, owner):
        super().__init__("drop", owner)

    def execute(self, argv):
        if self.validate_parameters(argv):
            name = argv[0]
            self.owner.drop_opserver(name)
        else:
            self.show_usage()

    def validate_parameters(self, params):
        return len(params) == 1

    def show_usage(self):
        print("%s [opserver] - drop operation server" % self.name)

class CUICommandInfoServer(CUICommand):
    def __init__(self, owner):
        super().__init__("info", owner)

    def execute(self, argv):
        self.owner.show_info_opserver()

    def show_usage(self):
        print("%s - show info of operation server" % self.name)

class CUICommandRunServer(CUICommand):
    def __init__(self, owner):
        super().__init__("run", owner)

    def execute(self, argv):
        if self.validate_parameters(argv):
            name = argv[0]
            self.owner.run_opserver(name)
        else:
            self.show_usage()

    def validate_parameters(self, params):
        return len(params) == 1

    def show_usage(self):
        print("%s [opserver] - run operation server" % self.name)

class CUICommandStopServer(CUICommand):
    def __init__(self, owner):
        super().__init__("stop", owner)

    def execute(self, argv):
        if self.validate_parameters(argv):
            name = argv[0]
            self.owner.stop_opserver(name)
        else:
            self.show_usage()

    def validate_parameters(self, params):
        return len(params) == 1

    def show_usage(self):
        print("%s [opserver] - stop operation server" % self.name)

class CUICommandRunAllServer(CUICommand):
    def __init__(self, owner):
        super().__init__("runall", owner)

    def execute(self, argv):
        self.owner.run_all_opserver()

    def show_usage(self):
        print("%s - run all operation server" % self.name)

class CUICommandStopAllServer(CUICommand):
    def __init__(self, owner):
        super().__init__("stopall", owner)

    def execute(self, argv):
        self.owner.stop_all_opserver()

    def show_usage(self):
        print("%s - stop all operation server" % self.name)
