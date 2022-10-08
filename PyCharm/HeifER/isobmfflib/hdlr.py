# -*- coding: utf-8 -*-
from .box import FullBox
from .box import Quantity
from .box import indent
from .box import read_int
from .box import read_string


class HandlerReferenceBox(FullBox):
    box_type = 'hdlr'
    is_mandatory = True
    quantity = Quantity.EXACTLY_ONE

    def __init__(self, size, version, flags, largesize, startByte):
        super().__init__(size=size, version=version, flags=flags, largesize=largesize, startByte=startByte)
        self.pre_defined = None
        self.handler_type = None
        self.reserved = []
        self.name = None

    def __repr__(self):
        rep = 'handler_type: ' + self.handler_type + '\n'
        rep += 'name: ' + self.name
        return super().__repr__() + indent(rep)

    def read(self, file, depth):
        self.depth = depth
        self.pre_defined = read_int(file, 4)
        self.handler_type = read_string(file, 4)
        bytesread = 8
        for _ in range(3): #3*4=12bytes
            self.reserved.append(read_int(file, 4))
            bytesread += 4
        self.name = read_string(file,self.get_box_size()-bytesread)               #NOTE: string read doesn't read enough characters, corrupting the following box read, extra char read added for Apple below

    def writeText(self, file, depth=0):
        super().writeText(file,depth)
        pad = " " * depth
        file.write(" {0}pre_defined={1}\n".format(pad, self.pre_defined))
        file.write(" {0}handler_type={1}\n".format(pad, self.handler_type))
        file.write(" {0}reserved={1}\n".format(pad, self.reserved))
        file.write(" {0}name={1}\n".format(pad, self.name))

