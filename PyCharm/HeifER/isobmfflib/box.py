# -*- coding: utf-8 -*-
import re
from enum import Enum
from . import log
import hashlib

padspaces = 7

class AbcBox(type):
    #TODO: human readable implementation of __repr__ 
    pass

class Box(object):
    box_type = None

    def __init__(self, size=None, largesize=None, startByte=None):
        self.size = size
        self.largesize = largesize
        self.startByte = startByte
        self.children = []
        self.BinaryData = None
        self.hash = None

    def __repr__(self):
        srep = super().__repr__()
        rep = '[start={0},end={1}]'.format(self.startByte,self.get_box_size_with_header())
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
                # if no box found, log the message and break this section of the loop
                log.writeln("Warning: Box not found at location {0} length {1}".format(current_position,read_size))
                break

            #store box
            setattr(self, box.box_type, box)  #store box in attribute
            self.children.append(box)         #append box the child list
            read_size -= box.size

    def writeText(self, file, depth=0):
        pad = " " * depth
        file.write("{0}Box Type={1}\n".format(pad, self.box_type))
        file.write("{0} Size={1}\n".format(pad, self.get_box_size_with_header()))
        file.write("{0} StartByte={1}\n".format(pad, self.startByte))
        file.write("{0} Children={1}\n".format(pad, len(self.children)))
        file.write("{0} Hash={1}\n".format(pad, self.hash))

    def writeData(self, file):
        file.write(self.BinaryData)

    def write(self, file, depth=0, writeText=True, writeData=False, recurse=True):
        if writeText:
            self.writeText(file,depth)
            file.write("\n")

        if writeData:
            self.writeData()
            file.write("\n")

        if recurse:
            for child in self.children:
                child.write(file,depth+1,writeText,writeData,recurse)


    def getBinaryDataFromFile(self,infile):
        start = self.startByte
        length = self.get_box_size_with_header()

        #get the binary data from the file and calculate the hash
        infile.seek(start)
        self.BinaryData = infile.read(length)
        self.hash = hashlib.md5(self.BinaryData).hexdigest()

        log.writeln("{0}:{1}{2} Hash={3}".format(str(start).rjust(6), "-" * self.depth, self.box_type, self.hash))

    def writeMapEntry(self,file,depth):
        indent = "-" * depth
        file.write("{0}:{1}{2}(size={3}, start={4}, end={5}, hash={6})\n".format(str(self.startByte).zfill(6), indent, self.box_type, self.get_box_size_with_header(), self.startByte, self.startByte+self.get_box_size_with_header(), self.hash))
        for childbox in self.children:
            childbox.writeMapEntry(file,depth+1)


class FullBox(Box):
    box_type = None

    def __init__(self, size, version=None, flags=None, largesize=None, startByte=None):
        super().__init__(size,largesize,startByte)
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

    def writeText(self, file, depth=0):
        super().writeText(file,depth)
        pad = " " * depth
        file.write("{0} Version={1}\n".format(pad, self.version))
        file.write("{0} Flags={1}\n".format(pad, self.flags))




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

    pad = "-" * depth
    log.writeln("{0}:{1}{2}(size={3}, start={4}, end={5})".format(str(current_position).rjust(padspaces),pad,box_type,printboxsize,current_position,current_position+printboxsize))
    box_classes = get_class_list(Box)
    box = None
    for box_class in box_classes:
        if box_class.box_type == box_type:
            box = box_class.__new__(box_class)
            if box_class.__base__.__name__ == 'FullBox':
                version = read_int(file, 1)
                flags = read_int(file, 3)
                box.__init__(size=box_size, version=version, flags=flags, largesize=largesize, startByte=current_position)
            else:
                box.__init__(size=box_size, largesize=largesize, startByte=current_position)

            if box.get_box_size():
                box.read(file, depth+1)
            break                       #NOTE: failed to here as iref box was not defined
        else:
            box = None

    if box == None:
        log.writeln("{0}:{1}No definition found for box type {2}. Contents = {3}".format(str(current_position).rjust(padspaces),pad,box_type,file.read(box_size-8)))

    return box
