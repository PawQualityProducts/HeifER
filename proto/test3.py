import sys
iFileName = sys.argv.index('-f')
iStartIndex = sys.argv.index('-i')

class Box:
    def __init__(self,bytes,index):
      self.size = int.from_bytes(bytes[index:index+4], byteorder='big')
      self.type = bytes[index+4:index+8].decode("utf-8")
      self.data = bytes[index+9:self.size-8]


def openfile(fname):
    with open(fname, mode='rb') as file:
        content = file.read()
    return content

if iFileName > 0 and iStartIndex > 0:
    fileBytes = openfile(sys.argv[iFileName+1])
    aBox = Box(fileBytes,int(sys.argv[iStartIndex+1]))

    print(aBox.size, aBox.type)
    print(aBox.data)


