import os
import copy

def read_int(file, length):
    return int.from_bytes(file.read(length), byteorder='big', signed=False)

def read_string(file, length=None):
    if length:
        res = file.read(length).decode()
    else:
        res = ''
        res = res.join(iter(lambda: file.read(1).decode('ascii'), '\x00'))
    return res

def ReadBoxHeader(infile,level):
    location = infile.tell()
    boxSize = read_int(infile,4)                       #read size (string, 4 bytes)
    boxType = read_string(infile,4)                 #read type (int, 4 bytes)
    print("{0}:{1}{2} {3}".format(str(location).zfill(8),' ' * level, boxType,str(boxSize)))
    boxheader = boxTypes[boxType](infile,level,boxType,boxSize)     #create an instance of a box
    return boxheader

class Box(object):
    def __init__(self, infile, level, type, size):
        self.level = level
        self.type = type
        self.size = size
        self.location = infile.tell() - 8
        if size == 0:                                       #this is a large box, so read box size from next 8 bytes
            self.largesize = read_int(infile,8)
        elif size == 1:                                     #box extends to end of the file
            self.largesize = infile.length - self.location
        else:
            self.largesize = None
        self.headerdata = b''
        self.children = []


    def getSize(self):
        if self.largesize:
            return self.largesize
        else:
            return self.size

    def start(self):
        return self.location

    def end(self):
        return self.location + self.getSize()

    def read(self,infile):
        self.headerdata = infile.read(self.end() - infile.tell())     #default read to the end of the box
        print("        {0}{1}".format('--' * self.level,self.headerdata))

    def readChildren(self,infile):
        location = infile.tell()
        while infile.tell() <= self.end():
            childBoxHeader = ReadBoxHeader(infile,self.level+1)
            self.children.append(childBoxHeader)
            childBoxHeader.read(infile)

    def writeheader(self,outfile):
        outfile.write((self.size).to_bytes(4, "big"))
        outfile.write(bytes(self.type, 'utf-8'))
        if self.size == 0:  # this is a large box, so read box size from next 8 bytes
            outfile.write((self.size).to_bytes(8, "big"))

    def writedata(self,outfile):
        if len(self.headerdata) > 0:
            outfile.write(self.headerdata)

    def writechildren(self,outfile):
        for child in self.children:
            child.write(outfile)

    def write(self,outfile):
        self.writeheader(outfile)
        self.writedata(outfile)
        self.writechildren(outfile)


    def serialize(self):
        bytes1 = self.serialize_header()
        bytes1 += self.serialize_data()
        bytes1 += self.serialize_children()
        return bytes1

    def serialize_header(self):
        bytes1 = (self.size).to_bytes(4, "big")
        bytes1 +=  bytes(self.type, 'utf-8')
        if self.size == 0:  # this is a large box, so read box size from next 8 bytes
            bytes1 += (self.size).to_bytes(8, "big")
        return bytes1

    def serialize_data(self):
        return self.headerdata

    def serialize_children(self):
        bytes2 = b''
        for child in self.children:
            bytes2 += child.serialize()
        return bytes2


class FullBox(Box):
    def __init__(self,infile ,level ,type, size):
        super().__init__(infile,level,type,size)
        self.version = read_int(infile,1)
        self.flags = read_int(infile,3)

    def writeheader(self,outfile):
        super().writeheader(outfile)
        outfile.write((self.version).to_bytes(1,"big"))
        outfile.write((self.flags).to_bytes(3, "big"))

    def serialize_header(self):
        bytes1 = super().serialize_header()
        bytes1 += (self.version).to_bytes(1,"big")
        bytes1 += (self.flags).to_bytes(3, "big")
        return bytes1

class ftypeBox(Box):
    pass

class metaBox(FullBox):
    def read(self,infile):
        #no further header data to read
        self.readChildren(infile)   #read child boxes

    #todo serialize


class mdatBox(FullBox):
    def read(self,infile):
        self.headerdata = infile.read(self.end() - infile.tell())     #default read to the end of the box
        print("        {0}mdat".format('--' * self.level))

    # todo serialize

class hdlrBox(FullBox):
    pass

class dinfBox(Box):
    def read(self,infile):
        #no further header data to read
        self.readChildren(infile)   #read child boxes

    #todo serialize

class drefBox(FullBox):
    pass

class pitmBox(FullBox):
    pass

class iinfBox(FullBox):
    def read(self,infile):
        self.item_count = read_int(infile,2 if self.version == 0 else 4)

        for item in range(self.item_count):
            childBoxHeader = ReadBoxHeader(infile,self.level+1)
            self.children.append(childBoxHeader)
            childBoxHeader.read(infile)

    def writeheader(self,outfile):
        super().writeheader(outfile)
        outfile.write((self.item_count).to_bytes(2 if self.version == 0 else 4,"big"))

    #todo serialize



class infeBox(FullBox):
    def read(self,infile):
        if self.version == 0 or self.version == 1:
            self.item_id = read_int(infile, 2)
            self.item_protection_index = read_int(infile, 2)
            self.item_name = read_string(infile)
            self.content_type = read_string(infile)
            self.content_encoding = read_string(infile)

            if self.version == 1:
                extension_type = read_string(infile)
                fdel = FDItemInfoExtension()
                fdel.read(infile)
                self.item_extension = fdel
        elif self.version >= 2:
            if self.version == 2:
                self.item_id = read_int(infile, 2)
            elif self.version == 3:
                self.item_id = read_int(infile, 4)
            self.item_protection_index = read_int(infile, 2)
            self.item_type = read_string(infile, 4)
            self.item_name = read_string(infile)

            if self.item_type == 'mime':
                self.content_type = read_string(infile)
                # self.content_encoding = read_string(file)         #NOTE: appears to remove an extra character corrupting the following box read
            elif self.item_type == 'uri ':
                self.uri_type = read_string(infile)

    def writeheader(self,outfile):
        super().writeheader(outfile)
        if self.version == 0 or self.version == 1:
            outfile.write((self.item_id).to_bytes(2, "big"))
            outfile.write((self.item_protection_index).to_bytes(2, "big"))
            outfile.write(bytes(self.item_name, 'utf-8'))
            outfile.write(bytes(self.content_type, 'utf-8'))
            outfile.write(bytes(self.content_encoding, 'utf-8'))

            if self.version == 1:
                outfile.write(bytes(self.extension_type, 'utf-8'))
                self.item_extension.writeheader(outfile)
        elif self.version >= 2:
            if self.version == 2:
                outfile.write((self.item_id).to_bytes(2, "big"))
            elif self.version == 3:
                outfile.write((self.item_id).to_bytes(4, "big"))
            outfile.write((self.item_protection_index).to_bytes(2, "big"))
            outfile.write(bytes(self.item_type, 'utf-8'))
            outfile.write(b'\x00')
            outfile.write(bytes(self.item_name, 'utf-8'))

            if self.item_type == 'mime':
                outfile.write(bytes(self.content_type, 'utf-8'))
                outfile.write(b'\x00')
            elif self.item_type == 'uri ':
                outfile.write(bytes(self.uri_type, 'utf-8'))
                outfile.write(b'\x00')


    def serialize_header(self):
        bytes1 = super().serialize_header()
        if self.version == 0 or self.version == 1:
            bytes1 += (self.item_id).to_bytes(2, "big")
            bytes1 += (self.item_protection_index).to_bytes(2, "big")
            bytes1 += bytes(self.item_name, 'utf-8')
            bytes1 += bytes(self.content_type, 'utf-8')
            bytes1 += bytes(self.content_encoding, 'utf-8')

            if self.version == 1:
                bytes1 += bytes(self.extension_type, 'utf-8')
                bytes1 += self.item_extension.serialize_header()
        elif self.version >= 2:
            if self.version == 2:
                bytes1 += (self.item_id).to_bytes(2, "big")
            elif self.version == 3:
                bytes1 += (self.item_id).to_bytes(4, "big")
            bytes1 += (self.item_protection_index).to_bytes(2, "big")
            bytes1 += bytes(self.item_type, 'utf-8')
            bytes1 += b'\x00'
            bytes1 += bytes(self.item_name, 'utf-8')

            if self.item_type == 'mime':
                bytes1 += bytes(self.content_type, 'utf-8')
                bytes1 += b'\x00'
            elif self.item_type == 'uri ':
                bytes1 += bytes(self.uri_type, 'utf-8')
                bytes1 += b'\x00'
        return bytes1

class FDItemInfoExtension(object):
    def __init__(self):
        self.content_location = None
        self.content_md5 = None
        self.content_length = None
        self.transfer_length = None
        self.group_ids = []

    def read(self, file):
        self.content_location = read_string(file)
        self.content_md5 = read_string(file)
        self.content_length = read_int(file, 8)
        self.transfer_length = read_int(file, 8)
        entry_count = read_int(file, 1)
        for _ in range(entry_count):
            group_id = read_int(file, 4)
            self.group_ids.append(group_id)

    def writeheader(self,outfile):
        outfile.write(bytes(self.content_location, 'utf-8'))
        outfile.write(bytes(self.content_md5, 'utf-8'))
        outfile.write((self.content_length).to_bytes(8,"big"))
        outfile.write((self.transfer_length).to_bytes(8,"big"))
        outfile.write((self.entry_count).to_bytes(1,"big"))
        for entry in self.group_ids:
            outfile.write((entry).to_bytes(4, "big"))

    def serialize_header(self):
        bytes1 = super().serialize_header()
        bytes1 += bytes(self.content_location, 'utf-8')
        bytes1 += bytes(self.content_md5, 'utf-8')
        bytes1 += (self.content_length).to_bytes(8,"big")
        bytes1 += (self.transfer_length).to_bytes(8,"big")
        bytes1 += (self.entry_count).to_bytes(1,"big")
        for entry in self.group_ids:
            bytes1 += (entry).to_bytes(4, "big")

        return bytes1



class irefBox(FullBox):
    def read(self,infile):
        super().read(infile)

class iprpBox(Box):
    def read(self,infile):
        super().read(infile)

class idatBox(Box):
    def read(self,infile):
        super().read(infile)

class ilocBox(FullBox):
    def read(self, infile):
        byte = read_int(infile, 1)
        self.offset_size = (byte >> 4) & 0b1111
        self.length_size = byte & 0b1111
        byte = read_int(infile, 1)
        self.base_offset_size = (byte >> 4) & 0b1111
        self.reserved = byte & 0b1111
        if self.version < 2:
            item_count = read_int(infile, 2)
        else:
            item_count = read_int(infile, 4)

        self.items = []

        for _ in range(item_count):
            item = {}
            if self.version < 2:
                item['item_id'] = read_int(infile, 2)
            else:
                item['item_id'] = read_int(infile, 4)

            if self.version in [1,2]:
                bytes = read_int(infile,2)
                item['reserved'] = bytes >> 4 & 0b111111111111
                item['construction_method'] =  bytes & 0b1111
            else:
                item['reserved'] = 0
                item['construction_method'] = 0

            item['data_reference_index'] = read_int(infile, 2)
            item['base_offset'] = read_int(infile, self.base_offset_size)
            extent_count = read_int(infile, 2)
            item['data'] = None
            item['extents'] = []

            print("        {0}item={1}".format('-' * self.level,item))
            for _ in range(extent_count):
                extent = {}
                extent['extent_offset'] = read_int(infile, self.offset_size)
                extent['extent_length'] = read_int(infile, self.length_size)
                item['extents'].append(extent)
                print("        {0}  extent={1}".format('-' * self.level, extent))
            self.items.append(item)
        pass

    def writeheader(self,outfile):
        super().writeheader(outfile)
        byte = (self.offset_size << 4) | self.length_size
        outfile.write((byte).to_bytes(1,"big"))
        byte = (self.base_offset_size << 4) | self.reserved
        outfile.write((byte).to_bytes(1,"big"))
        item_count = len(self.items)
        if self.version < 2:
            outfile.write((item_count).to_bytes(2,"big"))
        else:
            outfile.write((item_count).to_bytes(4, "big"))

        for item in self.items:
            if self.version < 2:
                outfile.write(item['item_id'].to_bytes(2,"big"))
            else:
                outfile.write(item['item_id'].to_bytes(4, "big"))

            if self.version in [1,2]:
                bytes = (item['reserved'] << 4) | item['construction_method']
                outfile.write((bytes).to_bytes(2, "big"))

            outfile.write((item['data_reference_index']).to_bytes(2,"big"))
            outfile.write((item['base_offset']).to_bytes(self.base_offset_size,"big"))
            outfile.write((len(item['extents']).to_bytes(2,"big")))

            for extent in item['extents']:
                outfile.write(extent['extent_offset'].to_bytes(self.offset_size, "big"))
                outfile.write(extent['extent_length'].to_bytes(self.length_size, "big"))

    def serialize_header(self):
        bytes1 = super().serialize_header()
        bytes1 += ((self.offset_size << 4) | self.length_size).to_bytes(1,"big")
        bytes1 += ((self.base_offset_size << 4) | self.reserved).to_bytes(1,"big")
        item_count = len(self.items)
        if self.version < 2:
            bytes1 += (item_count).to_bytes(2,"big")
        else:
            bytes1 += (item_count).to_bytes(4, "big")
        for item in self.items:
            bytes1 += self.serialize_iloc_item(item)


    def serialize_iloc_item(self,ilocitem):
        bytes1 = []
        if self.version < 2:
            bytes1 += ilocitem['item_id'].to_bytes(2, "big")
        else:
            bytes1 += ilocitem['item_id'].to_bytes(4, "big")

        if self.version in [1, 2]:
            bytes = (ilocitem['reserved'] << 4) | ilocitem['construction_method']
            bytes1 += (bytes).to_bytes(2, "big")

        bytes1 += (ilocitem['data_reference_index']).to_bytes(2, "big")
        bytes1 += (ilocitem['base_offset']).to_bytes(self.base_offset_size, "big")
        bytes1 += len(ilocitem['extents']).to_bytes(2, "big")

        for extent in ilocitem['extents']:
            bytes1 += extent['extent_offset'].to_bytes(self.offset_size, "big")
            bytes1 += extent['extent_length'].to_bytes(self.length_size, "big")
        return bytes1


boxTypes = {
    "ftyp" : ftypeBox,
    "meta" : metaBox,
    "mdat" : mdatBox,
    "hdlr" : FullBox,
    "dinf" : dinfBox,
    "dref" : drefBox,
    "pitm" : pitmBox,
    "iinf" : iinfBox,
    "infe" : infeBox,
    "iref" : irefBox,
    "iprp" : iprpBox,
    "idat" : idatBox,
    "iloc" : ilocBox
}


def boxsize(box):
    return len(box.serialize())


class HeifFile:
    def __init__(self):
        self.rootBoxHeaders = []

    def load(self,filename):
        infile = open(filename,'rb')                 # open the infile
        infile.length = os.stat(filename).st_size    # get the length of the file and add to file object

        while infile.tell() < infile.length:
            boxheader = ReadBoxHeader(infile,0)
            self.rootBoxHeaders.append(boxheader)
            boxheader.read(infile)
        infile.close()

    def save(self,filename):
        outfile = open(filename,'wb')
        for box in self.rootBoxHeaders:
            box.write(outfile)
        outfile.close()


    def find_meta_box(self):
        for box in self.rootBoxHeaders:
            if box.type == 'meta':
                return box

    def find_iinf_box(self):
        metabox = self.find_meta_box()
        for box in metabox.children:
            if box.type == 'iinf':
                return box

    def find_infe_box(self,id=None):
        iinfbox = self.find_iinf_box()
        for box in iinfbox.children:
            if box.item_id == id:
                return box

    def add_infe_box(self,infebox):
        metabox = self.find_meta_box()
        iinfbox = self.find_iinf_box()
        iinfbox.children.append(infebox)
        iinfbox.item_count += 1

        infeboxsize = len(infebox.serialize())
        iinfbox.size += infeboxsize
        metabox.size += infeboxsize

        return infeboxsize


    def add_iloc_item(self,ilocitem):
        metabox = self.find_meta_box()
        ilocbox = self.find_iloc_box()
        ilocbox.items.append(ilocitem)

        ilocitemsize = len(ilocbox.serialize_iloc_item(ilocitem))

        metabox.size += ilocitemsize
        ilocbox.size += ilocitemsize

        return ilocitemsize


    def adjust_iloc_item_offsets(self,adjustment):
        ilocbox = self.find_iloc_box()
        for item in ilocbox.items:
            if item['construction_method'] == 0:
                for extent in item['extents']:
                    extent['extent_offset'] += adjustment


    def find_iloc_box(self):
        metabox = self.find_meta_box()
        for box in metabox.children:
            if box.type == 'iloc':
                return box

    def find_iloc_item(self,id):
        ilocbox = self.find_iloc_box()
        for item in ilocbox.items:
            if item['item_id'] == id:
                return item

    def set_infe_box_id(self,infebox, id):
        infebox.item_id = id

    def set_iloc_item_id(self,ilocitem, id):
        ilocitem['item_id'] = id

    def find_mdat_box(self, nth=0):
        for box in self.rootBoxHeaders:
            if box.type == 'mdat':
                if nth <= 0:
                    return box
                else:
                    nth -= 1

