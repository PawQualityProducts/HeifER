import sys

def read_int(file, length):
    return int.from_bytes(file.read(length), byteorder='big', signed=False)

def read_string(file, length=None):
    if length:
        res = file.read(length).decode()
    else:
        res = ''
        res = res.join(iter(lambda: file.read(1).decode('ascii'), '\x00'))

def getflags(filename,boxOffset):
    infile = open(arg_infile,"rb+")
    infile.seek(boxOffset)
    size=read_int(infile,4)
    type=read_string(infile,4)
    if size==1:
        size=read_int(infile,8) #get large size
    version=read_int(infile,1)
    flags = infile.read(3)
    print("type={0}, flags={1}".format(type,flags))
    infile.close()
    return flags

def setflags(filename,boxOffset,flags):
    infile = open(arg_infile,"rb+")
    infile.seek(boxOffset)
    size=read_int(infile,4)
    type=read_string(infile,4)
    if size==1:
        size=read_int(infile,8) #get large size
    version=read_int(infile,1)
    infile.write(flags)
    print("type={0}, flags={1}".format(type,flags))
    infile.close()
    return flags

if __name__ == "__main__":
    arg_infile = sys.argv[1]
    arg_offset = sys.argv.index('-offset') if '-offset' in sys.argv[2:] else 0
    arg_flags = sys.argv.index('-flags') if '-flags' in sys.argv[2:] else 0

    if arg_infile and (arg_offset > 0):
        flags = getflags(arg_infile,int(sys.argv[arg_offset+1]))
        print(flags)
        if arg_flags:
            setflags(arg_infile,sys.argv[arg_offset+1],sys.argv[arg_flags+1])