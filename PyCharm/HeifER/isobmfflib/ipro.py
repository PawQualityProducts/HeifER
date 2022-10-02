# -*- coding: utf-8 -*-
from .box import FullBox
from .box import Quantity
from .box import read_box
from .box import read_int
from .box import read_string


class ItemProtectionBox(FullBox):
    box_type = 'ipro'
    is_mandatory = False
    quantity = Quantity.ZERO_OR_ONE

    def __init__(self, size, version, flags, largesize, startByte):
        super().__init__(size=size, version=version, flags=flags, largesize=largesize, startByte=startByte)
        self.protection_informations = []

    def __repr__(self):
        rep = super().__repr__()
        return rep

    def read(self, file, depth):
        self.depth = depth
        protection_count = read_int(file, 2)

        for _ in range(protection_count):
            box = read_box(file, depth+1)
            if not box:
                break
            if box.box_type == 'sinf':
                self.protection_informations.append(box)

    def writeText(self, file, depth=0):
        super().writeText(file, depth)
        pad = " " * depth
        file.write("{0} TODO: Implement writeText for {1}\n".format(pad,self.box_type))