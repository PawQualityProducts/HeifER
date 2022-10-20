import piexif
import os
import io

infile = open("/home/kali/samples/IMG_3802_test2.HEIC","rb")

#start=32002, end=34725

data = infile.read()

filestream = io.BytesIO(data[0:34722])


print(data[32002:34722])




