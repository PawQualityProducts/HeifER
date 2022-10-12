import sys


def read_bytes(file, length):
    return file.read(length)

def read_int(file, length):
    return int.from_bytes(file.read(length), byteorder='big', signed=False)

def read_string(file, length=None):
    if length:
        res = file.read(length).decode()
    else:
        res = ''
        res = res.join(iter(lambda: file.read(1).decode('ascii'), '\x00'))
    return res

def byte_list_to_hex_string(byte_list):
    return ''.join(format(x, '02x') for x in byte_list)

def hex_string_byte_list(hex_string):
    return bytes.fromhex(hex_string)


def getFlags(filename,boxOffset):
    infile = open(filename,"rb")
    infile.seek(boxOffset)
    size=read_int(infile,4)
    type=read_string(infile,4)
    if size==1:
        size=read_int(infile,8) #get large size
    version=read_int(infile,1)
    flags = infile.read(3)
    hexflags = byte_list_to_hex_string(flags)
    infile.close()
    return type,hexflags

def setFlags(filename,boxOffset,flags):
    infile = open(filename,"rb+")
    infile.seek(boxOffset)
    size=read_int(infile,4)
    type=read_string(infile,4)
    if size==1:
        size=read_int(infile,8) #get large size
    version=read_int(infile,1)
    bytes=hex_string_byte_list(flags)
    infile.write(bytes[0:3])
    infile.close()


if __name__ == "__main__":
    arg_infile = sys.argv[1]
    arg_offset = sys.argv.index('-offset') if '-offset' in sys.argv[2:] else 0
    arg_flags = sys.argv.index('-set') if '-set' in sys.argv[2:] else 0

    if arg_infile and (arg_offset > 0):
        if arg_flags:
            setFlags(arg_infile,int(sys.argv[arg_offset+1]),sys.argv[arg_flags+1])
        type, flags = getFlags(arg_infile, int(sys.argv[arg_offset + 1]))
        print("type={0}, flags={1}".format(type, flags))




