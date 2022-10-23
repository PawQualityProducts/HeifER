import copy
import heiffile2
import re

class HeifEditor(object):
    def __init__(self):
        pass

#-----------


if __name__ == '__main__':
    file1 = heiffile2.HeifFile()
    file1.load("/home/kali/samples/IMG_3802b.HEIC")

    urlboxes = file1.find_boxes("url ")
    print(urlboxes)

    urlboxes[0].flags=0
    urlboxes[0].binarydata = b'https://www.pawqualityproducts.co.uk/\x00'
    endbyte = file1.rebase()

    file1.save("/home/kali/samples/IMG_3802_test6.HEIC")
    pass