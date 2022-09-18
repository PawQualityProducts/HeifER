# -*- coding: utf-8 -*-
from .box import Box
from .box import FullBox
from .box import Quantity
from .box import read_box
from .box import read_int
from .box import read_string

"""
aligned(8) class ItemReferenceBox extends FullBox(‘iref’, version, 0) {
 if (version==0) {
 SingleItemTypeReferenceBox references[];
 } else if (version==1) {
 SingleItemTypeReferenceBoxLarge references[];
 }
}
"""

class ItemReferenceBox(FullBox):
    box_type = 'iref'
    is_mandatry = False
    quantity = Quantity.ZERO_OR_ONE
    references = []

    def __init__(self, size, version, flags, largesize):
        super().__init__(size, version, flags, largesize)

    def read(self, file):
        box_end_position = file.tell() + self.size - 12
        while file.tell() < box_end_position:
            current_position = file.tell()
            size = read_int(file, 4)
            type = read_string(file, 4)
            if self.version == 0:
                refBox = SingleItemTypeReferenceBox(type, size)
            else:
                refBox = SingleItemTypeReferenceBoxLarge(type, size)
            refBox.read(file)
            self.references.append(refBox)
            size += refBox.size
            print("  {0}:{1}({2})".format(current_position, type, size))


class SingleItemTypeReferenceBox(Box):
    def __init__(self, type, size):
        super().__init__(size)
        self.box_type = type
        self.references = []

    def read(self, file):
        self.from_item_ID = read_int(file, 2)
        self.reference_count = read_int(file, 2)
        for ref in range(self.reference_count):
            self.references.append(read_int(file, 2))

class SingleItemTypeReferenceBoxLarge(Box):
    def __init__(self, type, size):
        super().__init__(size)
        self.box_type = type
        self.references = []

    def read(self, file):
        self.from_item_ID = read_int(file, 4)
        self.reference_count = read_int(file, 2)
        for ref in range(self.reference_count):
            self.references.append(read_int(file, 4))

