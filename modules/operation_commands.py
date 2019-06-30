# coding=utf-8

from modules.operation_base import Command

class OperationHelp(Command):
    def __init__(self, owner):
        super().__init__("help", owner)
        self.aliases = ['?']

    def execute(self, argv):
        self.owner.list_all_cmd_usage()
        return True

    def show_usage(self):
        print("%s - show help" % self.name)

class OperationInfo(Command):
    def __init__(self, owner):
        super().__init__("info", owner)

    def execute(self, argv):
        self.owner.show_info()
        return True

    def show_usage(self):
        print("%s - show operation info" % self.name)

class OperationClientRun(Command):
    def __init__(self, owner):
        super().__init__("run", owner)

    def execute(self, argv):
        self.owner.start_client()
        return True

    def show_usage(self):
        print("%s - run operation client" % self.name)

class OperationClientStop(Command):
    def __init__(self, owner):
        super().__init__("stop", owner)

    def execute(self, argv):
        self.owner.stop_client()
        return True

    def show_usage(self):
        print("%s - stop operation client" % self.name)

class OperationServerRun(Command):
    def __init__(self, owner):
        super().__init__("run", owner)

    def execute(self, argv):
        self.owner.start_server()
        return True

    def show_usage(self):
        print("%s - run operation server" % self.name)

class OperationServerStop(Command):
    def __init__(self, owner):
        super().__init__("stop", owner)

    def execute(self, argv):
        self.owner.stop_server()
        return True

    def show_usage(self):
        print("%s - stop operation server" % self.name)

class OperationListEndpoint(Command):
    def __init__(self, owner):
        super().__init__("list", owner)

    def execute(self, argv):
        self.owner.list_endpoint()
        return True

    def show_usage(self):
        print("%s - list all operation endpoint" % self.name)

class OperationCloseEndpoint(Command):
    def __init__(self, owner):
        super().__init__("close", owner)

    def execute(self, argv):
        if self.validate_parameters(argv):
            name = argv[0]
            self.owner.close_endpoint(name)
            return True
        else:
            self.show_usage()
            return False

    def validate_parameters(self, params):
        return len(params) > 0

    def show_usage(self):
        print("%s <name> - close operation endpoint" % self.name)

class OperationSelectEndpoint(Command):
    def __init__(self, owner):
        super().__init__("select", owner)

    def execute(self, argv):
        name = argv[0] if len(argv) > 0 else None
        self.owner.select(name)
        return True

    def show_usage(self):
        print("%s [name] - select operation endpoint" % self.name)

class OperationEndpointUnselect(Command):
    def __init__(self, owner):
        super().__init__("unselect", owner)

    def execute(self, argv):
        self.owner.unselect()
        return True

    def show_usage(self):
        print("%s - unselect operation endpoint" % self.name)
