# coding=utf-8

from modules.operation_base import OperationBase

class OperationPing(OperationBase):
    def __init__(self, owner, hdr):
        super().__init__('ping', owner, hdr)
        self.ping_magic = None
        self.pong = None

    def execute(self, conn, argv):
        if self.validate_parameters(argv):
            self.ping_magic = argv[0] if len(argv) > 0 else None
            self.send_request(conn)
        else:
            self.show_usage()

    def validate_parameters(self, params):
        return len(params) <= 1

    def pack(self):
        data = super().pack()
        if self.ping_magic:
            data += struct_pack_string(self.ping_magic)
        return data

    def unpack(self):
        super().unpack()
        self.pong, = struct_unpack_string(self.hdr.payload())

    def show_usage(self):
        print('ping [MAGIC]')

    def show_request(self):
        pass

    def show_response(self):
        pass
