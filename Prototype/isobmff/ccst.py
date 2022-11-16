# -*- coding: utf-8 -*-
from .box import Box


class ccst(Box):
    box_type = 'ccst'
    is_mandatory = False

    def read(self, file, depth):
        self.depth = depth
        pad = '-' * depth
        print(pad + file.read(self.get_box_size()))