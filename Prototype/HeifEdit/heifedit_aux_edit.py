import copy
import heiffile
import re

class HeifEditor(object):
    def __init__(self):
        pass

#-----------

def stegoEncode(dataByteArray,startIndex,data):
  index = startIndex
  for dataByte in data:
    for bitIndex in range(8):
      value = dataByteArray[index]
      bitValue = dataByte >> bitIndex & 1
      newValue = value | bitValue
      print("index={0} : Value={1} : Byte={2} : BitIndex={3} : Bit={4} : NewValue={5}".format(index,value,dataByte,bitIndex,bitValue,newValue))
      dataByteArray[index] = newValue
      index += 1

def SimpleStegoEncode(dataByteArray,startIndex,step,data):
  index = startIndex
  for dataByte in data:
    print("index={0} : value={1} : newvalue={2}".format(index,dataByteArray[index],dataByte))
    dataByteArray[index] = dataByte
    index += step
    

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
    
    # alter original 
    SimpleStegoEncode(auxfiledata,100,8,b'PawQualityProducts.co.uk')
    
    #stegoEncode(auxfiledata,100,b'PawQualityProducts.co.uk');
    
    
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

    file1.save("/home/kali/samples/IMG_3221_aux_edited.heic")


