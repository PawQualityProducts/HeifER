# -*- coding: utf-8 -*-
from .box import FullBox
from .box import read_int
from .box import indent


class ItemLocationBox(FullBox):
    box_type = 'iloc'
    is_mandatory = False

    def __init__(self, size, version, flags, largesize, startByte):
        super().__init__(size=size, version=version, flags=flags, largesize=largesize, startByte=startByte)
        self.offset_size = None
        self.length_size = None
        self.base_offset_size = None
        self.reserved = None
        self.items = []

    def __repr__(self):
        rep = 'offset_size:' + str(self.offset_size) + '\n'
        rep += 'length_size:' + str(self.length_size)
        return super().__repr__() + indent(rep)

    def read(self, file, depth):
        self.depth = depth
        startByte = file.tell()
        byte = read_int(file, 1)
        self.offset_size = (byte >> 4) & 0b1111
        self.length_size = byte & 0b1111
        byte = read_int(file, 1)
        self.base_offset_size = (byte >> 4) & 0b1111
        self.reserved = byte & 0b1111
        if self.version < 2:
            item_count = read_int(file,2)
        else:
            item_count = read_int(file,4)

        self.items = []

        pad = "-" * depth
        #print("{0}{1}{2}:offset={1}, length={2}, base_offset_size={3}, reserved={4}, item_count={5} ".format(str(startByte).rjust(5),pad,self.box_type, self.offset_size, self.length_size, self.base_offset_size, self.reserved, item_count))
        for _ in range(item_count):
            item = {}
            if self.version < 2:
                item['item_id'] = read_int(file, 2)
            else:
                item['item_id'] = read_int(file, 4)
            if self.version in [1,2]:
                bytes = read_int(file,2)
                item['reserved'] = bytes >> 4 & 0b111111111111
                item['construction_method'] = 0b1111
            item['data_reference_index'] = read_int(file, 2)
            item['base_offset'] = read_int(file, self.base_offset_size)
            extent_count = read_int(file, 2)
            item['extents'] = []
            for _ in range(extent_count):
                extent = {}
                extent['extent_offset'] = read_int(file, self.offset_size)
                extent['extent_length'] = read_int(file, self.length_size)
                item['extents'].append(extent)
            self.items.append(item)


    def writeText(self, file, depth=0):
        super().writeText(file, depth)
        pad = " " * depth
        file.write("{0} TODO: Implement writeText for {1}\n".format(pad,self.box_type))
