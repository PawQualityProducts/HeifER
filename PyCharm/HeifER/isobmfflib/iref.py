# -*- coding: utf-8 -*-
from .box import Box
from .box import FullBox
from .box import Quantity
from .box import read_box
from .box import read_int
from .box import read_string
from . import log
import os

padspaces = 7

class ItemReferenceBox(FullBox):
    box_type = 'iref'
    is_mandatry = False
    quantity = Quantity.ZERO_OR_ONE
    references = []

    def __init__(self, size, version, flags, largesize, startByte):
        super().__init__(size, version, flags, largesize, startByte=startByte)

    def read(self, file, depth):
        self.depth = depth
        box_end_position = file.tell() + self.size - 12
        while file.tell() < box_end_position:
            current_position = file.tell()
            size = read_int(file, 4)
            type = read_string(file, 4)
            if self.version == 0:
                refBox = SingleItemTypeReferenceBox(type, size, current_position)
            else:
                refBox = SingleItemTypeReferenceBoxLarge(type, size, current_position)
            refBox.read(file, depth+1)
            self.references.append(refBox)
            self.children.append(refBox)
            size += refBox.size
            pad = "-" * depth
            log.writeln("{0}:{1}{2}(size={3}, start={4}, end={5})".format(str(current_position).rjust(padspaces), pad, type, refBox.size, current_position, current_position + refBox.size))

    def getBinaryDataFromFile(self,infile):
        super().getBinaryDataFromFile(infile)
        for ref in self.references:
            ref.getBinaryDataFromFile(infile)


    def writeText(self, file, depth=0):
        super().writeText(file, depth)
        pad = " " * depth
        file.write("{0} references={1}\n".format(pad, len(self.references)))
        refIndex = 0
        for ref in self.references:
            refIndex += 1
            file.write("{0}  reference={1}\n".format(pad, str(refIndex).zfill(3)))
            ref.writeText(file,depth+3)


class SingleItemTypeReferenceBox(Box):
    def __init__(self, type, size, startByte):
        super().__init__(size=size, startByte=startByte)
        self.box_type = type
        self.references = []

    def read(self, file, depth):
        self.depth = depth
        self.from_item_ID = read_int(file, 2)
        self.reference_count = read_int(file, 2)
        for ref in range(self.reference_count):
            self.references.append(read_int(file, 2))

    def writeText(self, file, depth=0):
        super().writeText(file, depth)
        pad = " " * depth
        file.write("{0} from_item_id={1}\n".format(pad, self.from_item_ID))
        file.write("{0} to_item_ids={1}\n".format(pad, self.references))


class SingleItemTypeReferenceBoxLarge(Box):
    def __init__(self, type, size, largesize, startByte):
        super().__init__(size, largesize, startByte)
        self.box_type = type
        self.references = []

    def read(self, file, depth):
        self.depth = depth
        self.from_item_ID = read_int(file, 4)
        self.reference_count = read_int(file, 2)
        for ref in range(self.reference_count):
            self.references.append(read_int(file, 4))

    def writeText(self, file, depth=0):
        super().writeText(file, depth)
        pad = " " * depth
        file.write("{0} TODO: Implement writeText for {1}\n".format(pad, self.box_type))


