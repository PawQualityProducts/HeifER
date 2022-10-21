import copy
import heiffile
import re

class HeifEditor(object):
    def __init__(self):
        pass

#-----------


if __name__ == '__main__':
    file1 = heiffile.HeifFile()
    file1.load("/home/kali/samples/IMG_3802b.HEIC")

    endbyte = file1.rebase()

    file1.save("/home/kali/samples/IMG_3802_test.HEIC")

    #copy image tile 47 and add as image item 54 -------------
    metaBox = file1.find_meta_box()
    iinfBox = file1.find_iinf_box()
    ilocBox = file1.find_iloc_box()

    infeBox47 = file1.find_infe_box(id=47)
    ilocEntry47 = file1.find_iloc_item(id=47)
    ipmaEntry47 = file1.find_ipma_item(id=47)

    newinfebox = copy.deepcopy(infeBox47)
    newilocitem = copy.deepcopy(ilocEntry47)
    newipmaitem = copy.deepcopy(ipmaEntry47)

    file1.set_infe_box_id(newinfebox, 54)
    file1.set_iloc_item_id(newilocitem,54)
    file1.set_impa_item_id(newipmaitem,54)

    file1.add_infe_box(newinfebox)
    file1.add_iloc_item(newilocitem)
    file1.add_impa_item(newipmaitem)

    endbyte = file1.rebase()

    file1.save("/home/kali/samples/IMG_3802_test2.HEIC")

    #dupliacte exif -------------------------------------------
    infeBox53 = file1.find_infe_box(id=53)
    ilocEntry53 = file1.find_iloc_item(id=53)

    itemrefbox53 = file1.find_iref_item_box(4)

    newinfebox = copy.deepcopy(infeBox53)
    newilocitem = copy.deepcopy(ilocEntry53)
    itemrefbox = copy.deepcopy(itemrefbox53)

    file1.set_infe_box_id(newinfebox, 55)
    file1.set_iloc_item_id(newilocitem,55)
    itemrefbox.from_item_ID = 55
    itemrefbox.references[0] = 54

    file1.add_iref_item_box(itemrefbox)
    file1.add_infe_box(newinfebox)
    file1.add_iloc_item(newilocitem)

    newdataoffset =  file1.rebase()

    mdatBox = file1.find_mdat_box(0)
    mdatoffset = mdatBox.startByte
    mdatdataoffset = mdatoffset + 12
    dataoffset = newilocitem['extents'][0]['extent_offset']
    datalength = newilocitem['extents'][0]['extent_length']

    copystart = dataoffset - mdatdataoffset
    copyend = copystart + datalength
    copydata = mdatBox.binarydata[copystart:copyend]

    x = re.compile(b'.*Apple\x00')
    pat = x.match(copydata)

    end = pat.regs[0][1]
    print(copydata[end-6:end])
    newdata = copydata[:end-6] + b"*Fake*" + copydata[end:]

    mdatBox.binarydata += newdata

    file1.rebase()

    newilocitem['extents'][0]['extent_offset'] = newdataoffset

    file1.rebase()

    file1.save("/home/kali/samples/IMG_3802_test3.HEIC")

    # try to insert a jpeg

    #copy image tile 47 and add as image item 56 and repurpose for jpeg-------------

    infeBox47 = file1.find_infe_box(id=47)
    ilocEntry47 = file1.find_iloc_item(id=47)

    newinfebox = copy.deepcopy(infeBox47)
    newilocitem = copy.deepcopy(ilocEntry47)

    file1.set_infe_box_id(newinfebox,56)
    file1.set_iloc_item_id(newilocitem,56)

    newinfebox.item_type = 'jpeg'

    file1.add_infe_box(newinfebox)
    file1.add_iloc_item(newilocitem)

    newdataoffset = file1.rebase()

    #load jpeg data
    jpegfile = open("/home/kali/samples/Anonymous.jpg","rb")
    jpegfiledata = jpegfile.read()

    print("mdat start={0}, length={1}".format(mdatBox.startByte,len(mdatBox.binarydata)))
    #append jpeg data to end of mdat box
    mdatBox.binarydata += jpegfiledata
    file1.rebase()

    print("jpeg start={0}, length={1}".format(newdataoffset, len(jpegfiledata)))
    print("mdat start={0}, length={1}".format(mdatBox.startByte, len(mdatBox.binarydata)))

    newilocitem['extents'][0]['extent_offset'] = newdataoffset
    newilocitem['extents'][0]['extent_length'] = len(jpegfiledata)


    file1.save("/home/kali/samples/IMG_3802_test4.HEIC")

    pass