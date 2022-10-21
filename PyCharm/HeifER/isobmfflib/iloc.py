# -*- coding: utf-8 -*-
from .box import FullBox
from .box import read_int
from .box import indent
import hashlib
import os
from . import log


padspaces = 7

__metaBox = None
def setMetaBox(metaBox):
    global __metaBox
    __metaBox = metaBox
    pass

def getMetaBox():
    return __metaBox


class ItemLocationBox(FullBox):
    box_type = 'iloc'
    is_mandatory = False

    def __init__(self, size, version, flags, largesize, startByte):
        super().__init__(size=size, version=version, flags=flags, largesize=largesize, startByte=startByte)
        self.offset_size = None
        self.length_size = None
        self.base_offset_size = None
        self.reserved = None
        self.items = []

    def __repr__(self):
        rep = 'offset_size:' + str(self.offset_size) + '\n'
        rep += 'length_size:' + str(self.length_size)
        return super().__repr__() + indent(rep)

    def read(self, file, depth):
        self.depth = depth
        startByte = file.tell()
        byte = read_int(file, 1)
        self.offset_size = (byte >> 4) & 0b1111
        self.length_size = byte & 0b1111
        byte = read_int(file, 1)
        self.base_offset_size = (byte >> 4) & 0b1111
        self.reserved = byte & 0b1111
        if self.version < 2:
            item_count = read_int(file,2)
        else:
            item_count = read_int(file,4)

        self.items = []

        pad = "-" * depth
        itemIndex = 0
        for _ in range(item_count):
            current_location = file.tell()
            itemIndex += 1
            item = {}
            item['startByte'] = current_location
            if self.version < 2:
                item['item_id'] = read_int(file, 2)
            else:
                item['item_id'] = read_int(file, 4)

            if self.version in [1,2]:
                bytes = read_int(file,2)
                item['reserved'] = bytes >> 4 & 0b111111111111
                item['construction_method'] =  bytes & 0b1111
            else:
                item['reserved'] = 0
                item['construction_method'] = 0

            item['data_reference_index'] = read_int(file, 2)
            item['base_offset'] = read_int(file, self.base_offset_size)
            extent_count = read_int(file, 2)
            item['data'] = None
            item['extents'] = []

            log.writeln("{0}:{1}  item={2}".format(str(current_location).rjust(padspaces), pad, str(itemIndex)))
            extentIndex = 0
            for _ in range(extent_count):
                current_location = file.tell()
                extentIndex += 1
                extent = {}
                extent['startByte'] = current_location
                extent['extent_offset'] = read_int(file, self.offset_size)
                extent['extent_length'] = read_int(file, self.length_size)
                extent['data'] = None
                extent['length'] = file.tell() - current_location
                item['extents'].append(extent)
            self.items.append(item)
            log.writeln("{0}:{1}    extent={2}".format(str(current_location).rjust(padspaces), pad, str(extentIndex)))
            item['length'] = file.tell() - item['startByte']

    def writeText(self, file, depth=0):
        super().writeText(file, depth)
        pad = " " * depth

        file.write("{0} offset_size={1}\n".format(pad, self.offset_size))
        file.write("{0} length_size={1}\n".format(pad, self.length_size))
        file.write("{0} base_offset_size={1}\n".format(pad, self.base_offset_size))

        file.write("{0} reserved={1}\n".format(pad, self.reserved))
        file.write("{0} item_count={1}\n".format(pad, len(self.items)))

        for item in self.items:
            file.write("{0}   item_id={1}\n".format(pad, item['item_id']))
            if self.version in [1,2]:
                file.write("{0}    reserved={1}\n".format(pad, item['reserved']))
                if item['construction_method'] == 1:
                    file.write("{0}    construction_method={1} => idat box\n".format(pad, item['construction_method']))
                else:
                    file.write("{0}    construction_method={1} => mdat box, offset from beginning of file\n".format(pad, item['construction_method']))

            file.write("{0}    data_reference_index={1}\n".format(pad, item['data_reference_index']))
            file.write("{0}    base_offset={1}\n".format(pad, item['base_offset']))
            file.write("{0}    extents={1}\n".format(pad, len(item['extents'])))
            extent_index=0
            for extent in item['extents']:
                extent_index+=1
                file.write("{0}    extent={1}\n".format(pad, extent_index))
                file.write("{0}      extent_offset={1}\n".format(pad, extent['extent_offset']))
                file.write("{0}      extent_length={1}\n".format(pad, extent['extent_length']))
                if item['construction_method']:
                    file.write("{0}      extent in idata box at file offset={1}\n".format(pad, extent['idata_file_offset']))
                file.write("{0}      extent_hash={1}\n".format(pad, extent['hash']))



    def getBinaryDataFromFile(self,infile):
        super().getBinaryDataFromFile(infile)

        #self.BinaryData = b''
        itemIndex=0
        for item in self.items:
            itemIndex += 1
            #item.BinaryData = [0x00]
            itemoffset = item['base_offset']
            extentIndex=0
            for extent in item['extents']:
                extentIndex += 1
                extentoffset =  extent['extent_offset']
                extentlength = extent['extent_length']

                extent['data'] = 0b0
                if item['construction_method'] == 0:
                    infile.seek(itemoffset + extentoffset)
                    extent['data'] = infile.read(extentlength)
                elif item['construction_method'] == 1:
                    metabox = getMetaBox()
                    if metabox:
                        if hasattr(metabox,"idat"):
                            if metabox.idat:
                                extent['idata_file_offset'] = metabox.idat.idataStartByte + extentoffset
                                infile.seek(metabox.idat.idataStartByte + extentoffset)
                                extent['data'] = infile.read(extentlength)
                    else:
                        infile.seek(itemoffset + extentoffset)
                        extent['data'] = infile.read(extentlength)
                else:
                    extent['data'] = 0b0        #

                extent['hash'] = hashlib.md5(extent['data']).hexdigest()
                log.writeln("{0}:  {1}{2} Hash={3}".format("      ", " " * self.depth, "item={0}, extent={1}".format(itemIndex, extentIndex), extent['hash']))


    def writeData(self, file):
        super().writeData(file)
        itemindex = 0
        for item in self.items:
            itemindex += 1
            boxdir = os.path.dirname(file.name)
            itemdir = os.path.join(boxdir,str(itemindex).zfill(3) + '_item')
            os.makedirs(itemdir)

            #itemfilename = os.path.join(itemdir,str(itemindex).zfill(3) + '_item.bin')
            #itemfile = open(itemfilename,"wb")
            #itemfile.write(item.BinaryData)
            #itemfile.close()

            extentindex = 0
            for extent in item['extents']:
                extentindex+=1
                extentfilename = os.path.join(itemdir,str(extentindex).zfill(3) + "_extent.bin")
                extentfile = open(extentfilename,"wb")
                extentfile.write(extent['data'])
                extentfile.close()

    def writeMapEntry(self,file,depth):
        indent = "-" * depth
        file.write("{0}:{1}{2}(size={3}, start={4}, end={5}, items={6}, hash={7})\n".format(str(self.startByte).zfill(6), indent, self.box_type, self.get_box_size_with_header(), self.startByte, self.startByte+self.get_box_size_with_header(), len(self.items), self.hash))
        itemIndex = 0
        for item in self.items:
            itemIndex += 1
            extentIndex = 0
            itemStartByte = item['startByte']
            itemLength = item['length']
            itemEndByte = itemStartByte + itemLength
            file.write("{0}:{1}  Item={2}, (size={3}, start={4}, end={5}, extents={6}, id={7})\n".format(str(itemStartByte).zfill(6), indent, itemIndex, itemLength, itemStartByte, itemStartByte+itemLength,len(item['extents']),item['item_id']))
            for extent in item['extents']:
                extentIndex += 1
                extentStartByte = extent['startByte']
                extentLength = extent['length']
                extentEndByte = extentStartByte + extentLength
                # assume construction method 0 = offset from file start
                dataStartByte = item['base_offset'] + extent['extent_offset']
                if item['construction_method'] == 1:
                    metabox = getMetaBox()
                    dataStartByte = metabox.idat.idataStartByte + extent['extent_offset']
                    type='idat'
                else:
                    type='mdat'
                dataLength = extent['extent_length']
                dataEndByte = dataStartByte + dataLength
                hash = extent['hash']
                file.write("{0}:{1}    Extent={2} (size={3}, start={4}, end={5}, data=(type={6}, length={7}, start={8}, end={9}, hash={10})\n".format(str(extentStartByte).zfill(6), indent,extentIndex,extentLength,extentStartByte,extentEndByte,type,dataLength,dataStartByte,dataEndByte,hash))
