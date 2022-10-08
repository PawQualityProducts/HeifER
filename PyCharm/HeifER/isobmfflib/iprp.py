# -*- coding: utf-8 -*-
from .box import Box
from .box import FullBox
from .box import Quantity
from .box import read_int


class ItemPropertiesBox(Box):
    box_type = 'iprp'
    is_mandatry = False
    quantity = Quantity.ZERO_OR_ONE


class ItemPropertyContainer(Box):
    box_type = 'ipco'
    is_mandatry = True
    quantity = Quantity.EXACTLY_ONE

class ImageSpatialExtents(FullBox):
    box_type = 'ispe'

    def __init__(self, size, version, flags, largesize, startByte):
        super().__init__(size=size, version=version, flags=flags, largesize=largesize, startByte=startByte)
        self.width = None
        self.height = None

    def read(self, file, depth):
        self.depth = depth
        self.width = read_int(file, 4)
        self.height = read_int(file, 4)

    def writeText(self, file, depth=0):
        super().writeText(file, depth)
        pad = " " * depth
        file.write("{0} width={1}\n".format(pad,str(self.width)))
        file.write("{0} height={1}\n".format(pad, str(self.height)))


class PixelAspectRatio(Box):
    box_type = 'pasp'

    def read(self, file, depth):
        self.depth = depth
        pad = '-' * depth
        print(file.read(self.get_box_size()))



class ColorInformation(Box):
    box_type = 'colr'

    def read(self, file, depth):
        self.depth = depth
        pad = '-' * depth
        print(file.read(self.get_box_size()))



class PixelInformation(Box):
    box_type = 'pixi'

    def read(self, file, depth):
        self.depth = depth
        pad = '-' * depth
        print(file.read(self.get_box_size()))



class RelativeInformation(Box):
    box_type = 'rloc'

    def read(self, file, depth):
        self.depth = depth
        pad = '-' * depth
        print(file.read(self.get_box_size()))



#Note: Added ImageRotation
class ImageRotation(Box):
    box_type = 'irot'

    def read(self, file, depth):
        self.depth = depth
        pad = '-' * depth
        print(file.read(self.get_box_size()))



#Note: Added auxC
class AuxiliaryTypeProperty(Box):
    box_type = 'auxC'

    def read(self, file, depth):
        self.depth = depth
        pad = '-' * depth
        print(file.read(self.get_box_size()))



#TODO: Move this and implement idat
class ItemDataBox(Box):
    box_type = 'idat'

    def read(self, file, depth):
        self.depth = depth
        pad = '-' * depth
        self.idata = file.read(self.get_box_size())


class ItemPropertyAssociation(FullBox):
    box_type = 'ipma'
    is_mandatry = True
    quantity = Quantity.EXACTLY_ONE

    def __init__(self, size, version, flags, largesize, startByte):
        super().__init__(size=size, version=version, flags=flags, largesize=largesize, startByte=startByte)
        self.items = []

    def read(self, file, depth):
        self.depth = depth
        entry_count = read_int(file, 4)
        id_size = 2 if self.version < 1 else 4
        for _ in range(entry_count):
            item = {}
            item['id'] = read_int(file, id_size)
            association_count = read_int(file, 1)
            item['associations'] = []
            for __ in range(association_count):
                association = {}
                if self.flags & 0b1:
                    byte = read_int(file, 2)
                    association['essential'] = (byte >> 15) & 0b1
                    association['property_index'] = byte & 0b111111111111111
                else:
                    byte = read_int(file, 1)
                    association['essential'] = (byte >> 7) & 0b1
                    association['property_index'] = byte & 0b1111111
                item['associations'].append(association)
            self.items.append(item)

    def writeText(self, file, depth=0):
        super().writeText(file, depth)
        pad = " " * depth
        file.write("{0} TODO: Implement writeText for {1}\n".format(pad, self.box_type))


"""
#TODO: Move this to it's own module file
#TODO: Extend parsing of grpl box contents
class GroupsListBox(Box):
    box_type = 'grpl'

    def read(self, file, depth):
        print(file.read(self.get_box_size()))


#TODO: Move this to it's own module file
#TODO: Extend parsing of grpl box contents
class UdesBox(Box):
    box_type = 'udes'

    def read(self, file, depth):
        print(file.read(self.get_box_size()))

#TODO: Move this to it's own module file
#TODO: Extend parsing of grpl box contents
class SgpdBox(Box):
    box_type = 'sgpd'

    def read(self, file, depth):
        print(file.read(self.get_box_size()))


# TODO: Move this to it's own module file
# TODO: Extend parsing of grpl box contents
class SbgpBox(Box):
    box_type = 'sbgp'

    def read(self, file, depth):
        print(file.read(self.get_box_size()))

# TODO: Move this to it's own module file
# TODO: Extend parsing of grpl box contents
class TrefBox(Box):
    box_type = 'tref'

    def read(self, file, depth):
        print(file.read(self.get_box_size()))
"""