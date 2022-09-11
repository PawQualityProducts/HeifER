def openfile(fname):
    with open(fname, mode='rb') as file:
        content = file.read()
    return content

def getBoxSizeAndType(bytes,index):
    boxSize = int.from_bytes(bytes[index:index+4], byteorder='big')
    boxType = bytes[index+4:index+8].decode("utf-8")
    return boxSize,boxType

c = openfile('IMG_3802.HEIC')
boxSize,boxType = getBoxSizeAndType(c,0)

print(c[0:4])
print(c[4:8])

print (boxSize,boxType)

