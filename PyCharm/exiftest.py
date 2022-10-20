
import io
import exifread




def test(fname):
    infile = open(fname,"rb")
    data = infile.read()
    start = 32053
    end = 34773
    exifdata = data[start:end]
    print(data)
    ed = exifdata[10:]

    file_stream = io.BytesIO(ed)
    tags = exifread.process_file(file_stream, details=True, strict=False)
    for k, v in tags.items():
        print("{0}={1}\n".format(k, v))

test("/home/kali/samples/IMG_3802_test3.HEIC")
