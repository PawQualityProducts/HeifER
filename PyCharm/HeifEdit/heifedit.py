import copy
import heiffile

class HeifEditor(object):
    def __init__(self):
        pass

#-----------


if __name__ == '__main__':
    file1 = heiffile.HeifFile()
    file1.load("/home/kali/samples/IMG_3802b.HEIC")

    endbyte = file1.rebase()

    file1.save("/home/kali/samples/IMG_3802_test.HEIC")

    #copy image tile 47 and add as image item 54
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

    urlboxes = file1.find_boxes('infe')

    #dupliacte exif
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

    mdatBox.binarydata += copydata

    newilocitem['extents'][0]['extent_offset'] = newdataoffset

    file1.save("/home/kali/samples/IMG_3802_test3.HEIC")
    pass