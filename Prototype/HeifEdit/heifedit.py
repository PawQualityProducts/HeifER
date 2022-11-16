import copy
import heiffile
import re

class HeifEditor(object):
    def __init__(self):
        pass

#-----------


if __name__ == '__main__':
    file1 = heiffile.HeifFile()
    file1.load("/home/kali/samples/IMG_3802.HEIC")

    endbyte = file1.rebase()

    file1.save("/home/kali/samples/IMG_3802_test.HEIC")

    #Alter order of infe records

    iinfboxes = file1.find_boxes("iinf")

    temp = iinfboxes[0].children[0]
    iinfboxes[0].children[0] = iinfboxes[0].children[1]
    iinfboxes[0].children[1] = temp

    file1.save("/home/kali/samples/IMG_3802_test1.HEIC")

    #add another tile object
    #copy image tile 47 and add as image item 54 -------------
    metaBox = file1.find_meta_box()
    iinfBox = file1.find_iinf_box()
    ilocBox = file1.find_iloc_box()

    infeBox47 = file1.find_infe_box(id=47)
    ilocEntry47 = file1.find_iloc_item(id=47)
    ipmaEntry47 = file1.find_ipma_item(id=47)

    newinfebox = copy.deepcopy(infeBox47)
    newilocitem = copy.deepcopy(ilocEntry47)


    file1.set_infe_box_id(newinfebox, 54)
    file1.set_iloc_item_id(newilocitem,54)
    file1.set_impa_item_id(newipmaitem,54)

    file1.add_infe_box(newinfebox)
    file1.add_iloc_item(newilocitem)
    file1.add_impa_item(newipmaitem)

    endbyte = file1.rebase()

    file1.save("/home/kali/samples/IMG_3802_test2.HEIC")

    #add another exif record -------------------------------------------
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
    #alter exif data
    newdata = copydata[:end-6] + b"*Fake*" + copydata[end:]

    mdatBox.binarydata += newdata

    file1.rebase()

    newilocitem['extents'][0]['extent_offset'] = newdataoffset

    file1.rebase()

    file1.save("/home/kali/samples/IMG_3802_test3.HEIC")

    # insert a jpeg -------------------------------------

    #copy image tile 47 and add as image item 56 and repurpose for jpeg

    infeBox47 = file1.find_infe_box(id=47)
    ilocEntry47 = file1.find_iloc_item(id=47)
    ipmaEntry47 = file1.find_ipma_item(id=47)

    newinfebox2 = copy.deepcopy(infeBox47)
    newilocitem2 = copy.deepcopy(ilocEntry47)
    newipmaitem2 = copy.deepcopy(ipmaEntry47)

    file1.set_infe_box_id(newinfebox2,56)
    file1.set_iloc_item_id(newilocitem2,56)
    file1.set_impa_item_id(newipmaitem2, 56)

    newinfebox2.item_type = 'jpeg'

    file1.add_infe_box(newinfebox2)
    file1.add_iloc_item(newilocitem2)
    file1.add_impa_item(newipmaitem2)

    newdataoffset2 = file1.rebase()

    #load jpeg data
    jpegfile = open("/home/kali/samples/Anonymous.jpg","rb")
    jpegfiledata = jpegfile.read()

    print("mdat start={0}, length={1}".format(mdatBox.startByte,len(mdatBox.binarydata)))
    #append jpeg data to end of mdat box
    mdatBox.binarydata += jpegfiledata
    file1.rebase()

    print("jpeg start={0}, length={1}".format(newdataoffset2, len(jpegfiledata)))
    print("mdat start={0}, length={1}".format(mdatBox.startByte, len(mdatBox.binarydata)))

    #set the data offset for the jpeg location record
    newilocitem2['extents'][0]['extent_offset'] = newdataoffset2
    newilocitem2['extents'][0]['extent_length'] = len(jpegfiledata)

    file1.save("/home/kali/samples/IMG_3802_test4.HEIC")

    #Add external URL reference -------------------------------------------
    urlboxes = file1.find_boxes("url ")

    #clear internal content flag : NB: pyheif fails to load the file if this flag is not clear (0=external, 1=internal)
    urlboxes[0].flags=0
    urlboxes[0].binarydata = b'https://www.pawqualityproducts.co.uk/\x00'

    #rebase
    endbyte = file1.rebase()

    file1.save("/home/kali/samples/IMG_3802_test5.HEIC")


