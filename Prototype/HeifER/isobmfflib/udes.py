# -*- coding: utf-8 -*-
from .box import Box


class udes(Box):
    box_type = 'udes'
    is_mandatory = False

    def read(self, file, depth):
        self.depth = depth
        pad = '-' * depth
        self.rawdata = file.read(self.get_box_size())
        #print(rawdata)



