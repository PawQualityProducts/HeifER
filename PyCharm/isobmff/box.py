# -*- coding: utf-8 -*-
import re
from enum import Enum

padspaces = 7

class AbcBox(type):
    #TODO: human readable implementation of __repr__ 
    pass

class Box(object):
    box_type = None

    def __init__(self, size=None, largesize=None):
        self.size = size
        self.largesize = largesize

    def get_box_size(self):
        """get box size excluding header"""
        # Note: Added Extended box sizing
        if self.size > 1:               # box is standard size
            return self.size - 8        # return size field value - size-field (4 bytes) and box-type field (4 bytes)
        elif self.size == 0:            # box is extended size
            return self.largesize - 16  # return largesize field value - extended-size field (8 bytes) and box-type field (4 bytes)
        else:                           # size == 1, box extends to the end of the file
            return self.largesize - 8   # box extends to end of file and value was tored in largesize, but additional 8 bytes was not read

        #Note: This is in conflict with the spec. For the iPhone image file, Size == 1 (so large size), but large size == 0 (so extends to end of file)

    def read(self, file, depth=0):
        #current_position = file.tell()
        read_size = self.get_box_size()
        while read_size > 0:
            box = read_box(file,depth+1)
            if not box:
                type = read_string(file,4)
                print ('{0} couldn\'t read box of type={1} size={2}'.format(file.tell(), type, read_size))
                break
            #TODO: Quantityでそのままsetattrか配列にappendか分ける
            setattr(self, box.box_type, box)
            read_size -= box.size

    def write(self, file):
        """write box to file"""
        pass

class FullBox(Box):
    box_type = None

    def __init__(self, size, version=None, flags=None, largesize=None):
        super().__init__(size,largesize)
        self.version = version
        self.flags = flags

    def __repr__(self):
        srep = super().__repr__()
        rep = ' v' + str(self.version) + '\n'
        return re.sub('\n', rep, srep, flags=re.MULTILINE)

    def get_box_size(self):
        """get box size excluding header"""
        if self.size > 1:
            return self.size - 12           # return box size minus header
        elif self.size == 0:
            return self.largesize - 16      # return extended box size minus header
        else:                               # size == 1, box extends to the end of the file
            return self.largesize - 8       # box extends to the end of the file, value was stored in largesize but additional 8 bytes not read


class Quantity(Enum):
    ZERO_OR_ONE = 0
    EXACTLY_ONE = 1
    ONE_OR_MORE = 2
    ANY_NUMBER = 3

def read_int(file, length):
    return int.from_bytes(file.read(length), byteorder='big', signed=False)

def read_string(file, length=None):
    #TODO: convert utf8
    if length:
        res = file.read(length).decode()
    else:
        res = ''
        res = res.join(iter(lambda: file.read(1).decode('ascii'), '\x00'))
    return res

def indent(rep):
    return re.sub(r'^', '  ', rep, flags=re.M)

def get_class_list(cls, res=[]):
    subclasses = getattr(cls, '__subclasses__')()
    for subclass in subclasses:
        get_class_list(subclass, res)
    res.append(cls)
    return res

def read_box(file,depth=0):
    current_position = file.tell()
    box_size = read_int(file, 4)
    box_type = read_string(file, 4)

    # Added extended box sizing
    if box_size == 0:
        largesize = read_int(file,8)                     # box is extended (read additional 8 bytes after box type)
    elif box_size == 1:
        largesize = file.length - current_position       # box extends to end of the file, store it in largesize
    else:
        largesize = 0                                    # box is standard size

    #print(box_type + '(' + str(size) + ')')
    pad = "-" * depth
    print("{0}:{1}{2}({3}, {4})".format(str(current_position).rjust(padspaces),pad,box_type,box_size,current_position+box_size))
    box_classes = get_class_list(Box)
    box = None
    for box_class in box_classes:
        if box_class.box_type == box_type:
            box = box_class.__new__(box_class)
            if box_class.__base__.__name__ == 'FullBox':
                version = read_int(file, 1)
                flags = read_int(file, 3)
                box.__init__(size=box_size, version=version, flags=flags, largesize=largesize)
            else:
                box.__init__(size=box_size, largesize=largesize)
            if box.get_box_size():
                box.read(file, depth+1)
            break                       #NOTE: fails to here as iref box not defined
        else:
            box = None

    #if box == None:
    #    print("{0}:{1} not defined ({2}) : {3}".format(current_position, box_type, box_size, largesize))
    #    box = Box(size=box_size,largesize=largesize)

    return box
