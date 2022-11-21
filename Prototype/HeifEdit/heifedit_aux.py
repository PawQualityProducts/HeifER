import copy
import heiffile
import re

class HeifEditor(object):
    def __init__(self):
        pass

#-----------


if __name__ == '__main__':
    file1 = heiffile.HeifFile()
    file1.load("/home/kali/samples/IMG_3221.HEIC")

    # insert a jpeg -------------------------------------

    #copy image tile 47 and add as image item 56 and repurpose for jpeg

    ilocEntry51 = file1.find_iloc_item(id=51)

    #load alternative overlay from the extracted binary data
    auxfile = open("/home/kali/samples/processed/IMG_3802_test.HEIC.export/002_meta/008_iloc/051_item/001_extent.bin","rb")
    auxfiledata = bytearray(auxfile.read())
    auxfile.close()
    
    # rebase but just to get the end of the mdat box (which is where the new overlay data be placed)
    newdataoffset = file1.rebase()

    mdatBox = file1.find_mdat_box(0)
    print("mdat start={0}, length={1}".format(mdatBox.startByte,len(mdatBox.binarydata)))
    #append aux data to end of mdat box
    mdatBox.binarydata += auxfiledata
    file1.rebase()

    print("aux start={0}, length={1}".format(newdataoffset, len(auxfiledata)))
    print("mdat start={0}, length={1}".format(mdatBox.startByte, len(mdatBox.binarydata)))

    #set the data offset for the existing aux location record
    ilocEntry51['extents'][0]['extent_offset'] = newdataoffset
    ilocEntry51['extents'][0]['extent_length'] = len(auxfiledata)

    #rebase
    endbyte = file1.rebase()

    file1.save("/home/kali/samples/IMG_3221_aux.heic")


