# -*- coding: utf-8 -*-
from .box import Box


class MediaDataBox(Box):
    box_type = 'mdat'
    is_mandatory = False

    def __init__(self, size, largesize, startByte):
        super().__init__(size=size,largesize=largesize, startByte=startByte)
        self.data_offset = None

    def read(self, file, depth):
        self.depth = depth
        self.data_offset = file.tell()
        file.read(self.get_box_size())

    def writeText(self, file, depth=0):
        super().writeText(file, depth)
        pad = " " * depth


