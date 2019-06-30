# coding=utf-8

class Command(object):
    def __init__(self, name, owner):
        self.name = name
        self.owner = owner
        self.aliases = []

    def is_alias_cmd(self, cmd):
        return cmd in self.aliases

    def execute(self, argv):
        pass

    def validate_parameters(self, params):
        pass

    def show_usage(self):
        pass

class OperationBase(Command):
    def __init__(self, name, owner, hdr):
        super().__init__(name, owner)
        self.hdr = hdr

    def pack(self):
        data = self.hdr.pack()
        return data

    def unpack(self, data):
        self.hdr.unpack(data)

    def send_request(self, conn):
        conn.send_message(self.pack())

    def handle_response(self, data):
        self.unpack(data)
