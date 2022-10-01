# -*- coding: utf-8 -*-
import re
from enum import Enum
from . import output

padspaces = 7

class AbcBox(type):
    #TODO: human readable implementation of __repr__ 
    pass

class Box(object):
    box_type = None

    def __init__(self, size=None, largesize=None, location=None):
        self.size = size
        self.largesize = largesize
        self.location = location
        self.children = []
        self.data = None
        self.hash = None

    def __repr__(self):
        srep = super().__repr__()
        rep = '[start={0},end={1}]'.format(self.location,self.get_box_size_with_header())
        rep += 'size=' + str(self.get_box_size_with_header()) + '\n'
        return re.sub('\n', rep, srep, flags=re.MULTILINE)


    def get_box_size_with_header(self):
        if self.size > 1:
            return self.size
        else:
            return self.largesize

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
        self.depth = depth
        current_position = file.tell()
        read_size = self.get_box_size()
        while read_size > 0:
            box = read_box(file,depth)
            if not box:
                #type = read_string(file,4)
                #print ('{0} couldn\'t read box of size={1}'.format(file.tell(), read_size))
                # print(file.read(box_size - 8))
                break

            setattr(self, box.box_type, box)
            self.children.append(box)

            read_size -= box.size

    def write(self, file, depth=0, text=True, binary=False, hash=False):
        """write box to file"""
        if text:
            pad = " " * depth
            file.write("{0}Type={1}\n".format(pad,self.box_type))
            pad += 1
            file.write("{0}Size={1}\n".format(pad,self.get_box_size_with_header()))
            file.write("{0}Location={1}\n".format(pad,self.location))
            file.write("{0}Children={1}\n".format(pad,len(self.children)))

            for child in self.children:
                write(self,file,depth+1,text,binary,hash)
        pass

    def output(self):
        pad = "-" * self.depth
        rep = '{0}[start={1},end={2},depth={3}]\n'.format(pad,self.location,self.get_box_size_with_header(),self.depth)
        rep += pad + '--size=' + str(self.get_box_size_with_header()) + '\n'
        rep += pad + '--type=' + self.box_type + '\n'
        return rep


class FullBox(Box):
    box_type = None

    def __init__(self, size, version=None, flags=None, largesize=None, location=None):
        super().__init__(size,largesize,location)
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

    def output(self):
        pad = "-" * self.depth
        rep = '{0}[start={1},end={2},depth={3}]\n'.format(pad,self.location,self.get_box_size_with_header(),self.depth)
        rep += pad + '--size=' + str(self.get_box_size_with_header()) + '\n'
        rep += pad + '--type=' + self.box_type + '\n'
        rep += pad + '--version=' + str(self.version) + '\n'
        return rep



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

    if box_size > 1:
        printboxsize = box_size
    else:
        printboxsize = largesize

    #print(box_type + '(' + str(size) + ')')
    pad = "-" * depth
    output.writeln("{0}:{1}{2}(size={3}, start={4}, end={5})".format(str(current_position).rjust(padspaces),pad,box_type,printboxsize,current_position,current_position+printboxsize))
    #print("{0}:{1}{2}(size={3}, start={4}, end={5})".format(str(current_position).rjust(padspaces),pad,box_type,printboxsize,current_position,current_position+printboxsize))
    box_classes = get_class_list(Box)
    box = None
    for box_class in box_classes:
        if box_class.box_type == box_type:
            box = box_class.__new__(box_class)
            if box_class.__base__.__name__ == 'FullBox':
                version = read_int(file, 1)
                flags = read_int(file, 3)
                box.__init__(size=box_size, version=version, flags=flags, largesize=largesize, location=current_position)
            else:
                box.__init__(size=box_size, largesize=largesize, location=current_position)

            if box.get_box_size():
                box.read(file, depth+1)
#                output.writeln(box)
            break                       #NOTE: fails to here as iref box not defined
        else:
            box = None

    if box == None:
        #print("{0}:{1} not defined ({2}) : {3}".format(str(current_position).rjust(padspaces), box_type, box_size, largesize))
        #print("{0}:{1}No definition found for box type {2}. Contents = {3}".format(str(current_position).rjust(padspaces),pad,box_type,file.read(box_size-8)))
        output.writeln("{0}:{1}No definition found for box type {2}. Contents = {3}".format(str(current_position).rjust(padspaces),pad,box_type,file.read(box_size-8)),Details.BoxName)

    return box
