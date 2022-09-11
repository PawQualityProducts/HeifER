import sys
iFileName = sys.argv.index('-f')

def GetBoxType(bytes,index):
    return bytes[index+4:index+8].decode("utf-8")


def IsKnownBoxType(type):
    knownBoxTypes = {'ftyp','meta','mdat'}
    return type in knownBoxTypes


class Box:
    def __init__(self,bytes,index):
      self.size = int.from_bytes(bytes[index:index+4], byteorder='big')
      self.type = bytes[index+4:index+8].decode("utf-8")
      index += 8

      if self.size == 1:
          self.size = int.from_bytes(bytes[index:index+8], byteorder='big')
          index += 8
      elif self.size == 0:
          self.size = len(bytes)

      if self.type =='uuid':
          self.usertype = bytes[index:index+16]
          index += 16

      self.data = bytes[index:self.size - index]


def openfile(fname):
    with open(fname, mode='rb') as file:
        content = file.read()
    return content

def processBox(box,level):
    if box.type != 'mdat' and box.type != 'ftyp':
        aBox = Box(box.data,0)
        print(level,aBox.type,aBox.size)
        processBox(aBox,level+1)


if iFileName > 0:
    i = 0
    fileBytes = openfile(sys.argv[iFileName+1])
    while i < len(fileBytes):
        type = GetBoxType(fileBytes,i)
        if IsKnownBoxType(type):
            aBox = Box(fileBytes,i)
            print(aBox.type, i, aBox.size)
            i += aBox.size
        else:
            print(type)
            break
