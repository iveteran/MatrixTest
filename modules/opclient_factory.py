# coding=utf-8

from modules.cui import CUICommand
from modules.operation_client import OperationClient

class OpClientFactory(object):
    def __init__(self, loop, ui, host, port):
        self.loop = loop
        self.ui = ui
        self.host = host
        self.port = port
        self.opclient_map = {}
        self.current_opclient = None
        self.operation_list = []
        self.register_default_commands()

    def create_opclient(self, name, host = None, port = None):
        if name in self.opclient_map:
            print("Operation client %s already exists" % name)
        else:
            opclient = OperationClient(name, host or self.host, port or self.port, self, self.loop)
            self.opclient_map[name] = opclient
            #for operation in self.operation_list:
            #    opclient.register_operation(operation)

    def batch_create_opclient(self, name_prefix, begin_num, end_num, host = None, port = None):
        for idx in range(begin_num, end_num):
            name = name_prefix + str(idx)
            self.create_opclient(name, host, port)

    def close_opclient(self, name):
        if self.current_opclient and name == self.current_opclient.name:
            print("Can not close an opclient that in use currently")
        elif name in self.opclient_map:
            self.stop_opclient(name)
            del self.opclient_map[name]
        else:
            print("Operation client %s not exists" % name)

    def run_opclient(self, name):
        if name in self.opclient_map:
            self.opclient_map[name].start_client()
        else:
            print("Operation client %s not exists" % name)

    def run_all_opclient(self):
        for opclient in self.opclient_map.values():
            opclient.start_client()

    def stop_opclient(self, name = None):
        if name in self.opclient_map:
            self.opclient_map[name].stop_client()
        else:
            print("Operation client %s not exists" % name)

    def stop_all_opclient(self):
        for opclient in self.opclient_map.values():
            opclient.stop_client()

    def list_opclient2(self, pnum = 10):
        print("Operation clients[%d]: %s" % (len(self.opclient_map), self.opclient_map.keys()[:pnum]))

    def list_opclient(self, pnum = 0):
        count = 0
        for name in self.opclient_map:
            print(name)
            count += 1
            if pnum != 0 and count >= pnum:
                break
        print("total: %d, listed: %d" % (len(self.opclient_map), count))

    def select_opclient(self, name):
        if not name:
            self.current_opclient = None
            self.ui.pop_operation()
        elif name in self.opclient_map:
            self.current_opclient = self.opclient_map[name]
            self.ui.push_operation(self.current_opclient)
        else:
            print("Operation client %s not exists" % name)

    def execute(self, argv):
        return self.ui.execute(argv)

    def show_info_opclient(self):
        print("host: ", self.host)
        print("port: ", self.port)
        print("current opclient: ", self.current_opclient.name if self.current_opclient else '')

    def get_current_opclient(self):
        return self.current_opclient

    def get_current_operation(self):
        return self.get_current_opclient()

    def register_operation(self, operation):
        self.operation_list.append(operation)

    def register_default_commands(self):
        self.ui.register_command(CUICommandCreateClient(self))
        self.ui.register_command(CUICommandBatchCreateClient(self))
        self.ui.register_command(CUICommandDropClient(self))
        self.ui.register_command(CUICommandSelectClient(self))
        self.ui.register_command(CUICommandListClient(self))
        self.ui.register_command(CUICommandRunClient(self))
        self.ui.register_command(CUICommandStopClient(self))
        self.ui.register_command(CUICommandRunAllClient(self))
        self.ui.register_command(CUICommandStopAllClient(self))
        self.ui.register_command(CUICommandInfoClient(self))

class CUICommandCreateClient(CUICommand):
    def __init__(self, owner):
        super().__init__("create", owner)

    def execute(self, argv):
        if self.validate_parameters(argv):
            opclient_name = argv[0]
            host, port = argv[1].split(':') if len(argv) >= 2 else [None, None]
            self.owner.create_opclient(opclient_name, host, port)
            return True
        else:
            self.show_usage()
            return False

    def validate_parameters(self, params):
        if len(params) == 1:
            return True
        elif len(params) == 2:
            host, port = params[1].split(':')
            return port.isdigit()
        else:
            return False

    def show_usage(self):
        print("%s <name> [host:port] - create operation client" % self.name)

class CUICommandBatchCreateClient(CUICommand):
    def __init__(self, owner):
        super().__init__("batch_create", owner)

    def execute(self, argv):
        if self.validate_parameters(argv):
            name_prefix = argv[0]
            begin_num = int(argv[1])
            end_num = int(argv[2])
            host, port = argv[3].split(':') if len(argv) >= 4 else [None, None]
            self.owner.batch_create_opclient(name_prefix, begin_num, end_num, host, port)
            return True
        else:
            self.show_usage()
            return False

    def validate_parameters(self, params):
        if len(params) == 3:
            return params[1].isdigit() and params[2].isdigit()
        elif len(params) == 4:
            host, port = params[3].split(':')
            return port.isdigit()
        else:
            return False

    def show_usage(self):
        print("%s <name prefix> <begin num> <end num> [host:port] - batch create operation client" % self.name)

class CUICommandSelectClient(CUICommand):
    def __init__(self, owner):
        super().__init__("select", owner)

    def execute(self, argv):
        opclient_name = argv[0] if len(argv) > 0 else None
        self.owner.select_opclient(opclient_name)
        return True

    def show_usage(self):
        print("%s [opclient] - select operation client" % self.name)

class CUICommandListClient(CUICommand):
    def __init__(self, owner):
        super().__init__("list", owner)

    def execute(self, argv):
        if self.validate_parameters(argv):
            pnum = int(argv[0]) if len(argv) > 0 else 20
            self.owner.list_opclient(pnum)
            return True
        else:
            self.show_usage()
            return False

    def validate_parameters(self, params):
        return len(params) == 0 or (len(params) == 1 and params[0].isdigit())

    def show_usage(self):
        print("%s [print num] - list operation client" % self.name)

class CUICommandDropClient(CUICommand):
    def __init__(self, owner):
        super().__init__("close", owner)

    def execute(self, argv):
        if self.validate_parameters(argv):
            name = argv[0]
            self.owner.close_opclient(name)
            return True
        else:
            self.show_usage()
            return False

    def validate_parameters(self, params):
        return len(params) == 1

    def show_usage(self):
        print("%s [opclient] - close operation client" % self.name)

class CUICommandInfoClient(CUICommand):
    def __init__(self, owner):
        super().__init__("info", owner)

    def execute(self, argv):
        self.owner.show_info_opclient()
        return True

    def show_usage(self):
        print("%s - show info of operation client" % self.name)

class CUICommandRunClient(CUICommand):
    def __init__(self, owner):
        super().__init__("run", owner)

    def execute(self, argv):
        if self.validate_parameters(argv):
            name = argv[0]
            self.owner.run_opclient(name)
            return True
        else:
            self.show_usage()
            return False

    def validate_parameters(self, params):
        return len(params) == 1

    def show_usage(self):
        print("%s [opclient] - run operation client" % self.name)

class CUICommandStopClient(CUICommand):
    def __init__(self, owner):
        super().__init__("stop", owner)

    def execute(self, argv):
        if self.validate_parameters(argv):
            name = argv[0]
            self.owner.stop_opclient(name)
            return True
        else:
            self.show_usage()
            return False

    def validate_parameters(self, params):
        return len(params) == 1

    def show_usage(self):
        print("%s [opclient] - stop operation client" % self.name)

class CUICommandRunAllClient(CUICommand):
    def __init__(self, owner):
        super().__init__("runall", owner)

    def execute(self, argv):
        self.owner.run_all_opclient()
        return True

    def show_usage(self):
        print("%s - run all operation client" % self.name)

class CUICommandStopAllClient(CUICommand):
    def __init__(self, owner):
        super().__init__("stopall", owner)

    def execute(self, argv):
        self.owner.stop_all_opclient()
        return True

    def show_usage(self):
        print("%s - stop all operation client" % self.name)
