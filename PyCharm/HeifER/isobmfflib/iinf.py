# -*- coding: utf-8 -*-
from .box import FullBox
from .box import indent
from .box import read_box
from .box import read_int
from .box import read_string


class ItemInformationBox(FullBox):
    box_type = 'iinf'
    is_mandatory = False

    def __init__(self, size, version, flags, largesize, startByte):
        super().__init__(size=size, version=version, flags=flags, largesize=largesize, startByte=startByte)
        self.item_infos = []

    def __repr__(self):
        rep = 'entry_count: ' + str(len(self.item_infos)) + '\n'
        for item in self.item_infos:
            rep += item.__repr__()
        return super().__repr__() + indent(rep)

    def read(self, file, depth):
        self.depth = depth
        count_size = 2 if self.version == 0 else 4
        entry_count = read_int(file, count_size)

        for _ in range(entry_count):
            box = read_box(file, depth+1)
            if not box:
                break

            if box.box_type == 'infe':
                self.item_infos.append(box)

            self.children.append(box)
        pass

    def writeText(self, file, depth=0):
        super().writeText(file, depth)
        pad = " " * depth
        file.write("{0} Item Info Entries={1}\n".format(pad, len(self.item_infos)))
        for item_info in self.item_infos:
            item_info.write(file,depth+1)


class ItemInfomationEntry(FullBox):
    box_type = 'infe'

    def __init__(self, size, version, flags, largesize, startByte):
        super().__init__(size=size, version=version, flags=flags, largesize=largesize, startByte=startByte)
        self.item_id = None
        self.item_protection_index = None
        self.item_name = None
        self.item_extension = None
        self.item_type = None
        self.content_type = None
        self.content_encoding = None
        self.uri_type = None

    def __repr__(self):
        rep =  'item_id: ' + str(self.item_id) + '\n'
        rep += 'item_protection_index: ' + \
            str(self.item_protection_index) + '\n'
        rep += 'item_name: ' + self.item_name
        if self.version >= 2:
            rep += '\nitem_type: ' + str(self.item_type)
        return super().__repr__() + indent(rep)

    def read(self, file, depth):
        self.depth = depth
        if self.version == 0 or self.version == 1:
            self.item_id = read_int(file, 2)
            self.item_protection_index = read_int(file, 2)
            self.item_name = read_string(file)
            self.content_type = read_string(file)
            self.content_encoding = read_string(file)

            if self.version == 1:
                extension_type = read_string(file, 4)
                fdel = FDItemInfoExtension()
                fdel.read(file)
                self.item_extension = fdel
        elif self.version >= 2:
            if self.version == 2:
                self.item_id = read_int(file, 2)
            elif self.version == 3:
                self.item_id = read_int(file, 4)
            self.item_protection_index = read_int(file, 2)
            self.item_type = read_string(file, 4)
            self.item_name = read_string(file)
            
            if self.item_type == 'mime':
                self.content_type = read_string(file)
                #self.content_encoding = read_string(file)         #NOTE: appears to remove an extra character corrupting the following box read
            elif self.item_type == 'uri ':
                self.uri_type = read_string(file)

    def writeText(self, file, depth=0):
        super().writeText(file, depth)
        pad = " " * depth
        if self.flags & 1:
            file.write("{0} *** HIDDEN ***\n".format(pad))
        file.write("{0} item_id={1}\n".format(pad, self.item_id))
        file.write("{0} item_protection_index={1}\n".format(pad, self.item_protection_index))
        file.write("{0} item_name={1}\n".format(pad, self.item_name))
        file.write("{0} item_extension={1}\n".format(pad, self.item_extension))
        file.write("{0} item_type={1}\n".format(pad, self.item_type))
        file.write("{0} content_type={1}\n".format(pad, self.content_type))
        file.write("{0} content_encoding={1}\n".format(pad, self.content_encoding))
        file.write("{0} uri_type={1}\n".format(pad, self.uri_type))

    def writeMapEntry(self,file,depth):
        indent = "-" * depth
        if self.flags & 1:
            file.write("{0}:{1}{2}(size={3}, start={4}, end={5}, hash={6}, ***HIDDEN*** id={7})\n".format(str(self.startByte).zfill(6), indent, self.box_type, self.get_box_size_with_header(), self.startByte, self.startByte+self.get_box_size_with_header(), self.hash, self.item_id))
        else:
            file.write(
                "{0}:{1}{2}(size={3}, start={4}, end={5}, hash={6}, id={7})\n".format(str(self.startByte).zfill(6),
                                                                                      indent, self.box_type,
                                                                                      self.get_box_size_with_header(),
                                                                                      self.startByte,
                                                                                      self.startByte + self.get_box_size_with_header(),
                                                                                      self.hash, self.item_id))

        for childbox in self.children:
            childbox.writeMapEntry(file,depth+1)


class FDItemInfoExtension(object):
    def __init__(self):
        self.content_location = None
        self.content_md5 = None
        self.content_length = None
        self.transfer_length = None
        self.group_ids = []
    
    def read(self, file, depth):
        self.depth = depth
        self.content_location = read_string(file)
        self.content_md5 = read_string(file)
        self.content_length = read_int(file, 8)
        self.transfer_length = read_int(file, 8)
        entry_count = read_int(file, 1)
        for _ in range(entry_count):
            group_id = read_int(file, 4)
            self.group_ids.append(group_id)


    def writeText(self, file, depth=0):
        super().writeText(file, depth)
        pad = " " * depth
        file.write("{0} content_location={1}\n".format(pad, self.content_location))
        file.write("{0} content_md5={1}\n".format(pad, self.content_md5))
        file.write("{0} content_length={1}\n".format(pad, self.content_length))
        file.write("{0} transfer_length={1}\n".format(pad, self.transfer_length))
        file.write("{0} group_ids:\n".format(pad))
        for groupid in self.group_ids:
            file.write("{0} group_id={1}\n".format(pad, groupid))


#TODO: add iref here...