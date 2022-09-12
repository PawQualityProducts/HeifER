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
      "dinf" : DataInformationBox,
      "dref" : DataReferenceBox,
      "iinf" : ItemInfoBox,  #TODO: Create class for iinf
      "infe" : ItemInfoEntry  #TODO: Create class for infe
    }
    boxType = GetBoxType(bytes,index)
    box = boxTypes.get(boxType,Box)(bytes,index,level)
    pad = "-" * level
    print (pad + "CreateBox: index={0}, BoxType={1}, Level={2} : {3}".format(index,boxType,level,box.__class__))
    return box


class Box:
    def __init__(self,bytes,index, level=0):
        self.index = index
        self.level = level
        self.nextItem = 0
        self.size = int.from_bytes(bytes[index:index+4], byteorder='big')
        self.nextItem += 4
        self.type = bytes[index+self.nextItem:index+self.nextItem+4].decode("utf-8")
        self.nextItem += 4

        if self.size == 1:          # if size is 1 then get 64bit extended size
            self.size = int.from_bytes(bytes[index+self.nextItem:index+self.nextItem+8], byteorder='big')
            self.nextItem += 8
        elif self.size == 0:        # if size is 0, then box extends to end of file
             self.size = len(bytes)

        if self.type =='uuid':
            self.usertype = bytes[index+self.nextItem:index+self.nextItem+16]
            self.nextItem += 16
        else:
            self.usertype = None

        #self.data = bytes[index+self.nextItem:self.size-self.nextItem]

    def __str__(self):
        pad = "-" * self.level
        return pad + f'Box: index={self.index} type={self.type}, size={self.size}, usertype={self.usertype}'


class FullBox(Box):
    def __init__(self,bytes,index,level=0):
        Box.__init__(self,bytes,index,level)      #call base class __init__
        self.version = bytes[index+self.nextItem]    #int.from_bytes(bytes[index+self.nextItem], byteorder='big')
        self.nextItem += 1
        self.flags = bytes[index+self.nextItem:index+self.nextItem+3]
        self.nextItem += 3
        #self.data = bytes[index+self.nextItem:self.size-self.nextItem]

    def __str__(self):
        pad = "-" * self.level
        return pad + f'FullBox: index={self.index}, type={self.type}, size={self.size}, version={self.version}, flags={self.flags}, '


class FileTypeBox(Box):  #ftyp
    def __init__(self,bytes,index,level=0):
        Box.__init__(self,bytes,index)      #call base class __init__
        self.major_brand = bytes[index+self.nextItem:index+self.nextItem+4].decode("utf-8")
        self.nextItem += 4
        self.minor_version = int.from_bytes(bytes[index+self.nextItem:index+self.nextItem+4], byteorder='big')
        self.nextItem += 4
        self.compatible_brands = bytes[index+self.nextItem:index+self.nextItem+(self.size-self.nextItem)].decode("utf-8")

    def __str__(self):
        pad = "-" * self.level
        return pad + f'FileTypeBox: index={self.index}, type={self.type}, size={self.size}, major_brand={self.major_brand}, minor_version={self.minor_version}, compatible_brands={self.compatible_brands}'


class HandlerBox(FullBox):  #hdlr
    def __init__(self,bytes,index,level=0):
        FullBox.__init__(self,bytes,index,level)        #call base class __init__
        self.pre_defined = int.from_bytes(bytes[index+self.nextItem:index+self.nextItem+4], byteorder='big')
        self.nextItem += 4
        self.handler_type = bytes[index+self.nextItem:index+self.nextItem+4].decode("utf-8")
        self.nextItem += 4
        self.reserved = int.from_bytes(bytes[index+self.nextItem:index+self.nextItem+4], byteorder='big')
        self.nextItem += 4
        self.name = bytes[index+self.nextItem:index+self.nextItem+(self.size-self.nextItem)].decode("utf-8")

    def __str__(self):
        pad = "-" * self.level
        return pad + f'HandlerBox: type={self.type}, size={self.size}, pre_defined={self.pre_defined}, handler_type={self.handler_type}, reserved={self.reserved}, name={self.name}'


class MetaBox(FullBox):  #meta
    def __init__(self,bytes,index,level=0):
        FullBox.__init__(self,bytes,index,level)       #call base class __init__
        self.theHandler = CreateBox(bytes,index+self.nextItem,self.level+1)  # HandlerBox(bytes,index+self.nextItem)
        self.nextItem += self.theHandler.size
        while self.nextItem < self.size:
            box = CreateBox(bytes,index+self.nextItem,self.level+1)
            self.nextItem += box.size
            if box.type == "pitm":
                self.primary_resource = box
            if box.type == "dinf":
                self.item_locations = box
        #TODO: get the following sub-boxes if available in the byte stream
        self.item_locations = None     #ItemLocationBox(bytes,index)
        self.protections = None        #ItemProtectionBox(bytes,index)
        self.item_infos = None         #ItemInfoBox(bytes,index)
        self.IPMP_control = None       #IPMPControlBox(bytes,index)
        self.item_refs = None          #ItemReferenceBox(bytes,index)
        self.item_data = None          #ItemDataBox(bytes,index)

    def __str__(self):
        pad = "-" * self.level
        return pad + f'MetaBox: type={self.type}, size={self.size}, theHandler=({self.theHandler}) ..'  #TODO: add more


class PrimaryItemBox(FullBox):  #pitm
    def __init__(self,bytes,index,level=0):
        FullBox.__init__(self,bytes,index,level)       #call base class __init__
        if self.version == 0:
            self.item_ID = int.from_bytes(bytes[index+self.nextItem:index+self.nextItem+2], byteorder='big')
            self.nextItem += 2
        else:
            self.item_ID = int.from_bytes(bytes[index+self.nextItem:index+self.nextItem+4], byteorder='big')
            self.nextItem += 4

    def __str__(self):
        pad = "-" * self.level
        return pad + f'PrimaryItemBox: type={self.type}, size={self.size}, item_ID={self.item_ID}'


class DataInformationBox(Box):  #dinf
    def __init__(self,bytes,index,level=0):
        Box.__init__(self,bytes,index,level)       #call base class __init__
        self.data_reference = CreateBox(bytes,index+self.nextItem,self.level+1)
        self.nextItem += self.data_reference.size

    def __str__(self):
        pad = "-" * self.level
        return pad + f'DataInformationBox: index={self.index} type={self.type}, size={self.size}'


class DataEntryUrlBox(FullBox):  #url_
    def __init__(self,bytes,index,level=0):
        FullBox.__init__(self,bytes,index,level)    #call base class __init__
        self.location = bytes[index+self.nextItem:index+self.size-self.nextItem]  #TODO: get string location

    def __str__(self):
        pad = "-" * self.level
        return pad + f'DataEntryUrlBox: type={self.type}, size={self.size}, location={self.location}'


class DataEntryUrnBox(FullBox):  #urn_
    def __init__(self,bytes,index,level=0):
        FullBox.__init__(self,bytes,index,level)    #call base class __init__
        self.name = ""   #TODO: get string name and location
        self.location = bytes[index+self.nextItem:index+self.size-self.nextItem]

    def __str__(self):
        pad = "-" * self.level
        return pad + f'DataEntryUrnBox: type={self.type}, size={self.size}, name={self.name}, location={self.location}'


class DataReferenceBox(FullBox):  #dref
    def __init__(self,bytes,index,level=0):
        FullBox.__init__(self,bytes,index,level)    #call base class __init__
        self.entry_count = int.from_bytes(bytes[index+self.nextItem:index+self.nextItem+4], byteorder='big')
        self.nextItem += 4
        self.entries = []
        for x in range(self.entry_count):
            entry = CreateBox(bytes,index+self.nextItem,level+1)
            self.nextItem += entry.size
            self.entries.append(entry)

    def __str__(self):
        pad = "-" * self.level
        return pad + f'DataReferenceBox: type={self.type}, size={self.size}, entry_count={self.entry_count}'


class ItemInfoBox(FullBox):
    def __init__(self,bytes,index,level=0):
        FullBox.__init__(self,bytes,index,level)    #Call base constructor
        if self.version == 0:
            self.entry_count = int.from_bytes(bytes[index+self.nextItem:index+self.nextItem+2],byteorder='big')
            self.nextItem += 2
        else:
            self.entry_count = int.from_bytes(bytes[index+self.nextItem:index+self.nextItem+4],byteorder='big')
            self.nextItem += 4
        self.ItemInfoEntries = []
        for x in range(self.entry_count):
            entry = CreateBox(bytes,index+self.nextItem,level)
            self.nextItem += entry.size
            if entry.type == "infe":
                self.ItemInfoEntries.append(entry)


class ItemInfoEntry(FullBox):
    def __init__(self,bytes,index,level=0):
        FullBox.__init__(self,bytes,index,level)
        if(self.version == 0 or self.version == 1):
            self.item_ID = int.from_bytes(bytes[index+self.nextItem:index+self.nextItem+2])
            self.nextItem += 2
            self.item_protection_index = int.from_bytes(bytes[index+self.nextItem:index+self.nextItem+2])
            self.nextItem += 2
            self.name = ""               #TODO: get zero terminated string
            self.content_type = ""       #TODO: get zero terminated string
            self.content_encoding = ""   #TODO: get zero terminated string
            #TODO: Add rest of class ItemInfoEntry






#-----------------

def openfile(fname):
    with open(fname, mode='rb') as file:
        content = file.read()
    return content


if iFileName > 0:
    i = 0
    fileBytes = openfile(sys.argv[iFileName+1])
    while i < len(fileBytes):
        type = GetBoxType(fileBytes,i)
        if IsKnownBoxType(type):
            aBox = CreateBox(fileBytes,i,0)
            ##print(aBox.type, i, aBox.size, aBox.headerSize)
            #print(aBox)
            i += aBox.size
        else:
            print(type)
            break
