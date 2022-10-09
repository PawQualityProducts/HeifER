# -*- coding: utf-8 -*-
from .box import Box
from .box import FullBox
from .box import Quantity
from .box import read_box
from .box import read_int
from .box import read_string


class SampleTableBox(Box):
    box_type = 'stbl'
    is_mandatory = True
    quantity = Quantity.EXACTLY_ONE

class SampleDescriptionBox(FullBox):
    box_type = 'stsd'
    is_mandatory = True
    quantity = Quantity.EXACTLY_ONE    
    
    def __init__(self, size, version, flags, largesize, startByte):
        super().__init__(size=size, version=version, flags=flags, largesize=largesize, startByte=startByte)
        #self.handler_type = handler_type
        self.samples = []

    def read(self, file, depth):
        self.depth = depth
        entry_count = read_int(file, 4)
        for _ in range(entry_count):
            box = read_box(file, depth+1)
            if not box:
                break
            self.samples.append(box)
            self.children.append(box)

    def writeText(self, file, depth=0):
        super().writeText(file, depth)
        pad = " " * depth
        file.write("{0} entries={1}\n".format(pad, len(self.samples)))
        for sample in self.samples:
            sample.writeText(file,depth+1)


class SampleEntry(Box):
    def __init__(self, size, largesize, startByte):
        super().__init__(size=size, largesize=largesize, startByte=startByte)
        self.reserveds = []
        self.data_reference_index = None

    def __repr__(self):
        rep = super().__repr__()
        return rep

    def get_box_size(self):
        return super().get_box_size() - 6 + 2    

    def read(self, file, depth):
        self.depth = depth
        for _ in range(6):
            reserved = read_int(file, 1)
            self.reserveds.append(reserved)
        self.data_reference_index = read_int(file, 2)

    def writeText(self, file, depth=0):
        super().writeText(file, depth)
        pad = " " * depth
        file.write("{0} reserveds={1}\n".format(pad, self.reserveds))
        file.write("{0} data_reference_index={1}\n".format(pad, self.data_reference_index))


class HintSampleEntry(SampleEntry):
    """Hint Sample Entry
    """
    box_type = 'hint'

    def __init__(self, size, largesize, startByte):
        super().__init__(size=size, largesize=largesize, startByte=startByte)
        self.data = []

    def read(self, file, depth):
        self.depth = depth
        box_size = self.get_box_size()
        self.data = file.read(box_size)

    def writeText(self, file, depth=0):
        super().writeText(file, depth)
        pad = " " * depth
        #file.write("{0} TODO: Implement writeText for {1}\n".format(pad, self.box_type))


class VisualSampleEntry(SampleEntry):
    """Visual Sample Entry
    """
    box_type = 'vide'

    def __init__(self, size, largesize, startByte):
        super().__init__(size=size, largesize=largesize, startByte=startByte)
        self.pre_defined1 = None
        self.reserved1 = None
        self.pre_defined2 = []
        self.width = None
        self.height = None
        self.horizresolution = None
        self.vertresolution = None
        self.reserved2 = None
        self.frame_count = None
        self.compressorname = None
        self.depth = None
        self.pre_defined3 = None
    
    def read(self, file, depth):
        super().read(file, depth)
        self.pre_defined1 = read_int(file, 2)
        self.reserved1 = read_int(file, 2)
        for _ in range(3):
            self.pre_defined2.append(read_int(file, 4))
        self.width = read_int(file, 2)
        self.height = read_int(file, 2)
        self.horizresolution = read_int(file, 4)
        self.vertresolution = read_int(file, 4)
        self.reserved2 = read_int(file, 4)
        self.frame_count = read_int(file, 2)
        self.compressorname = read_string(file, 32)
        self.depth = read_int(file, 2)
        self.pre_defined3 = read_int(file, 2)

    def writeText(self, file, depth=0):
        super().writeText(file, depth)
        pad = " " * depth
        file.write("{0} pre_defined1={1}\n".format(pad, self.pre_defined1))
        file.write("{0} reserved1={1}\n".format(pad, self.reserved1))
        file.write("{0} width={1}\n".format(pad, self.width))
        file.write("{0} height={1}\n".format(pad, self.height))
        file.write("{0} horizresolution={1}\n".format(pad, self.horizresolution))
        file.write("{0} vertresolution={1}\n".format(pad, self.vertresolution))
        file.write("{0} reserved2={1}\n".format(pad, self.reserved2))
        file.write("{0} frame_count={1}\n".format(pad, self.frame_count))
        file.write("{0} compressorname={1}\n".format(pad, self.compressorname))
        file.write("{0} depth={1}\n".format(pad, self.depth))
        file.write("{0} pre_defined3={1}\n".format(pad, self.pre_defined3))


class AudioSampleEntry(SampleEntry):
    """Audio Sample Entry"""
    box_type = 'soun'

    def __init__(self, size, largesize, startByte):
        super().__init__(size=size, largesize=largesize, startByte=startByte)
        self.reserved1 = []
        self.channelcount = None
        self.samplesize = None
        self.pre_defined = None
        self.reserved2 = []
        self.samperate = None
    
    def read(self, file, depth):
        super().read(file)
        for _ in range(2):
            self.reserved1.append(read_int(file, 4))
        self.channelcount = read_int(file, 2)
        self.samplesize = read_int(file, 2)
        self.pre_defined = read_int(file, 2)
        for _ in range(2):
            self.reserved2.append(read_int(file, 2))
        self.samperate = read_int(file, 4)

    def writeText(self, file, depth=0):
        super().writeText(file, depth)
        pad = " " * depth
        file.write("{0} reserved1={1}\n".format(pad, self.reserved1))
        file.write("{0} channelcount={1}\n".format(pad, self.channelcount))
        file.write("{0} samplesize={1}\n".format(pad, self.samplesize))
        file.write("{0} pre_defined={1}\n".format(pad, self.pre_defined))
        file.write("{0} reserved2={1}\n".format(pad, self.reserved2))
        file.write("{0} samperate={1}\n".format(pad, self.samperate))


class BitRateBox(Box):
    """Bit Rate Box"""
    box_type = 'btrt'

    def __init__(self, size, largesize, startByte):
        super().__init__(size=size, largesize=largesize, startByte=startByte)
        self.buffer_size_db = None
        self.max_bitrate = None
        self.avg_bitrate = None

    def read(self, file, depth):
        self.depth = depth
        self.buffer_size_db = read_int(file, 4)
        self.max_bitrate = read_int(file, 4)
        self.avg_bitrate = read_int(file, 4)

    def writeText(self, file, depth=0):
        super().writeText(file, depth)
        pad = " " * depth
        file.write("{0} buffer_size_db={1}\n".format(pad, self.buffer_size_db))
        file.write("{0} max_bitrate={1}\n".format(pad, self.max_bitrate))
        file.write("{0} avg_bitrate={1}\n".format(pad, self.avg_bitrate))



