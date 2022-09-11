
class Box:
    def __init__(self,bytes,index):
      self.size = int.from_bytes(bytes[index:index+4], byteorder='big')
      self.type = bytes[index+4:index+8].decode("utf-8")
      self.data = bytes[index+9:self.size-8]


def openfile(fname):
    with open(fname, mode='rb') as file:
        content = file.read()
    return content

c = openfile('IMG_3802.HEIC')
aBox = Box(c,0)

print(aBox.size, aBox.type)
print(aBox.data)


