# -*- coding: utf-8 -*-
from .box import Box


class MediaDataBox(Box):
    box_type = 'mdat'
    is_mandatory = False

    def __init__(self, size, largesize):
        super().__init__(size=size,largesize=largesize)
        self.data_offset = None

    def read(self, file, depth):
        self.data_offset = file.tell()
        file.read(self.get_box_size())
