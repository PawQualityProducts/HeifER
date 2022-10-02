# -*- coding: utf-8 -*-
from .box import FullBox
from .box import indent
from .box import read_int


class PrimaryItemBox(FullBox):
    box_type = 'pitm'
    is_mandatory = False

    def read(self, file, depth):
        self.depth = depth
        self.item_id = read_int(file, 2)

    def writeText(self, file, depth=0):
        super().writeText(file, depth)
        pad = " " * depth
        file.write("{0} TODO: Implement writeText for {1}\n".format(pad, self.box_type))

