# coding=utf-8

from modules.operation_base import OperationBase

class OperationEcho(OperationBase):
    def __init__(self, owner, hdr):
        super().__init__('echo', owner, hdr)
        self.echo_msg = None
        self.echo_rsp = None

    def execute(self, conn, argv):
        if self.validate_parameters(argv):
            self.echo_msg = argv[0]
            self.send_request(conn)
        else:
            self.show_usage()

    def validate_parameters(self, params):
        return len(params) == 1

    def pack(self):
        data = super().pack()
        data += struct_pack_string(self.echo_msg)
        return data

    def unpack(self):
        super().unpack()
        self.echo_rsp, = struct_unpack_string(self.hdr.payload())

    def show_usage(self):
        print('echo <MESSAGE>')

    def show_request(self):
        pass

    def show_response(self):
        pass
