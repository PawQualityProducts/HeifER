import sys
iFileName = sys.argv.index('-f')

def GetBoxType(bytes,index):
    return bytes[index+4:index+8].decode("utf-8")

def IsKnownBoxType(type):
    knownBoxTypes = {'ftyp','meta','mdat','pitm'}
    return type in knownBoxTypes

def CreateBox(bytes,index,level):
    boxTypes = {
      "????" : Box,
      "ftyp" : FileTypeBox,
      "meta" : MetaBox,
      "hdlr" : HandlerBox,
      "pitm" : PrimaryItemBox,
      "url " : DataEntryUrlBox,
      "urn " : DataEntryUrnBox,
      "dinf" : DataInformationBox
    }
    boxType = GetBoxType(bytes,index)
    print ("CreateBox : index={0}, BoxType={1}, Level={2}".format(index,boxType,level))
    return boxTypes.get(boxType,Box)(bytes,index,level)


class Box:
    def __init__(self,bytes,index,level=0):
        self.level=level
        self.headerSize = 0
        self.size = int.from_bytes(bytes[index:index+4], byteorder='big')
        self.headerSize += 4
        self.type = bytes[index+self.headerSize:index+8].decode("utf-8")
        self.headerSize += 4

        if self.size == 1:
            self.size = int.from_bytes(bytes[index+self.headerSize:index+self.headerSize+8], byteorder='big')
            self.headerSize += 8
        elif self.size == 0:
             self.size = len(bytes)

        if self.type =='uuid':
            self.usertype = bytes[index+self.headerSize:index+self.headerSize+16]
            self.headerSize += 16
        else:
            self.usertype = None

        #self.data = bytes[index+self.headerSize:self.size-self.headerSize]

    def __str__(self):
        return ('-'*self.level) + f'Box: type={self.type}, size={self.size}, usertype={self.usertype}'


class FullBox(Box):
    def __init__(self,bytes,index,level=0):
        Box.__init__(self,bytes,index)
        self.version = bytes[index+self.headerSize]    #int.from_bytes(bytes[index+self.headerSize], byteorder='big')
        self.headerSize += 1
        self.flags = bytes[index+self.headerSize:index+self.headerSize+3]
        self.headerSize += 3
        #self.data = bytes[index+self.headerSize:self.size-self.headerSize]

    def __str__(self):
        return ('-'*self.level) + f'FullBox: type={self.type}, size={self.size}, version={self.version}, flags={self.flags}, '


class FileTypeBox(Box):  #ftyp
    def __init__(self,bytes,index,level=0):
        Box.__init__(self,bytes,index)
        self.major_brand = int.from_bytes(bytes[index+self.headerSize:index+self.headerSize+4], byteorder='big')
        self.headerSize += 4
        self.minor_version = int.from_bytes(bytes[index+self.headerSize:index+self.headerSize+4], byteorder='big')
        self.headerSize += 4
        self.compatible_brandes = bytes[:self.size-self.headerSize]

    def __str__(self):
        return ('-'*self.level) + f'FileTypeBox: type={self.type}, size={self.size}, major_brand={self.major_brand}, minor_version={self.minor_version} ..'


class HandlerBox(FullBox):  #hdlr
    def __init__(self,bytes,index,level=0):
        FullBox.__init__(self,bytes,index)
        self.pre_defined = int.from_bytes(bytes[index+self.headerSize:index+self.headerSize+4], byteorder='big')
        self.headerSize += 4
        self.handler_type = int.from_bytes(bytes[index+self.headerSize:index+self.headerSize+4], byteorder='big')
        self.headerSize += 4
        self.reserved = int.from_bytes(bytes[index+self.headerSize:index+self.headerSize+4], byteorder='big')
        self.headerSize += 4
        self.name = bytes[index+self.headerSize:self.size-self.headerSize]

    def __str__(self):
        return ('-'*self.level) + f'HandlerBox: type={self.type}, size={self.size}, pre_defined={self.pre_defined}, handler_type={self.handler_type}, reserved={self.reserved}, name={self.name}'


class MetaBox(FullBox):  #meta
    def __init__(self,bytes,index,level=0):
        FullBox.__init__(self,bytes,index)
        self.theHandler = CreateBox(bytes,index+self.headerSize,self.level+1)  # HandlerBox(bytes,index+self.headerSize)
        self.headerSize += self.theHandler.size
        self.primary_resource = None   #PrimaryItemBox(bytes,index)
        self.file_locations = None     #DataInformationBox(bytes,index)
        self.item_locations = None     #ItemLocationBox(bytes,index)
        self.protections = None        #ItemProtectionBox(bytes,index)
        self.item_infos = None         #ItemInfoBox(bytes,index)
        self.IPMP_control = None       #IPMPControlBox(bytes,index)
        self.item_refs = None          #ItemReferenceBox(bytes,index)
        self.item_data = None          #ItemDataBox(bytes,index)

    def __str__(self):
        return ('-'*self.level) + f'MetaBox: type={self.type}, size={self.size}, theHandler=({self.theHandler}) ..'  #TODO: add more


class PrimaryItemBox(FullBox):  #pitm
    def __init__(self,bytes,index,level=0):
        FullBox.__init__(self.bytes,index)
        if self.version == 0:
            self.item_ID = int.from_bytes(bytes[index+self.headerSize:index+self.headerSize+2], byteorder='big')
            self.headerSize += 2
        else:
            self.item_ID = int.from_bytes(bytes[index+self.headerSize:index+self.headerSize+4], byteorder='big')
            self.headerSize += 4

    def __str__(self):
        return ('-'*self.level) + f'PrimaryItemBox: type={self.type}, size={self.size}, item_ID={self.item_ID}'


class DataInformationBox(Box):  #dinf
    def __init__(self,bytes,index,level=0):
        Box.__init__(self,bytes,index)

    def __str__(self):
        return ('-'*self.level) + f'DataInformationBox: type={self.type}, size={self.size}'


class DataEntryUrlBox(FullBox):  #url_
    def __init__(self,bytes,index,level=0):
        FullBox.__init__(self,bytes,index)
        self.location = bytes[index+self.headerSize:index+self.size-self.headerSize]  #TODO: get string location

    def __str__(self):
        return ('-'*self.level) + f'DataEntryUrlBox: type={self.type}, size={self.size}, location={self.location}'


class DataEntryUrnBox(FullBox):  #urn_
    def __init__(self,bytes,index,level=0):
        FullBox.__init__(self,bytes,index)
        self.name = ""                                                                    #TODO: get string name and location
        self.location = bytes[index+self.headerSize:index+self.size-self.headerSize]

    def __str__(self):
        return ('-'*self.level) + f'DataEntryUrnBox: type={self.type}, size={self.size}, name={self.name}, location={self.location}'


class DataReferenceBox(FullBox):  #dref
    def __init__(self,bytes,index):
        FullBox.__init__(self,bytes,index,level=0)
        self.entry_count = int.from_bytes(bytes[index+self.headerSize:index+self.headerSize+4], byteorder='big')
        self.headerSize += 4
        self.entries = []
        for x in range(self.entry_count):
            entry = CreateBox(self,bytes,index+self.headerSize)
            self.headerSize += entry.size
            self.entries.append(entry)

    def __str__(self):
        return ('-'*self.level) + f'DataReferenceBox: type={self.type}, size={self.size}, entry_count={self.entry_count}'


#-----------------

def openfile(fname):
    with open(fname, mode='rb') as file:
        content = file.read()
    return content

def processBox(box,level):
    if box.type != 'mdat' and box.type != 'ftyp':
        aBox = Box(box.data,0)
        print(level,aBox.type,aBox.size, aBox.headerSize)
        processBox(aBox,level+1)


if iFileName > 0:
    i = 0
    fileBytes = openfile(sys.argv[iFileName+1])
    while i < len(fileBytes):
        type = GetBoxType(fileBytes,i)
        if IsKnownBoxType(type):
            aBox = CreateBox(fileBytes,i,0)
            ##print(aBox.type, i, aBox.size, aBox.headerSize)
            print(i,aBox)
            i += aBox.size
        else:
            print(type)
            break
