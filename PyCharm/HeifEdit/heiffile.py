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
        super().read(infile)

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

            print("        {0}item={1}\n".format('-' * self.level,item))
            for _ in range(extent_count):
                extent = {}
                extent['extent_offset'] = read_int(infile, self.offset_size)
                extent['extent_length'] = read_int(infile, self.length_size)
                item['extents'].append(extent)
                print("        {0}  extent={1}\n".format('-' * self.level, extent))
            self.items.append(item)

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

        #TODO: Serialize Header


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


    def find_meta_Box(self):
        for box in self.rootBoxHeaders:
            if box.type == 'meta':
                return box

    def find_iinf_Box(self,MetaBox):
        for box in MetaBox.children:
            if box.type == 'iinf':
                return box

    def find_infe_Box(self,IinfBox,id=None,nth=0):
        if nth > 0 and nth < len(InfBox.children):
            return InfBox.children[nth-1]
        elif id != None:
            for box in IinfBox.children:
                if box.id == id:
                    return box

    def add_infe_Box(self,InfeBox):
        MetaBox = self.findMetaBox()
        IinfBox = self.findIinfBox(MetaBox)
        IinfBox.children.append(InfeBox)
        IinfBox.item_count += 1
        size = len(InfeBox.serialize())
        IinfBox.size += size
        MetaBox.size += size
        #todo update offset locations for iloc items, add size

    def find_iloc_Box(self,MetaBox):
        for box in MetaBox.children:
            if box.type == 'iloc':
                return box

    def find_mdat_Box(self, nth=0):
        for box in self.rootBoxHeaders:
            if box.type == 'mdat':
                if nth <= 0:
                    return box
                else:
                    nth -= 1



