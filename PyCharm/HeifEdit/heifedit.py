import copy
import heiffile

class HeifEditor(object):
    def __init__(self):
        pass

#-----------


if __name__ == '__main__':
    file1 = heiffile.HeifFile()
    file1.load("/home/kali/samples/IMG_3802b.HEIC")
    file1.save("/home/kali/samples/IMG_3802_test.HEIC")

    metaBox = file1.find_meta_box()
    iinfBox = file1.find_iinf_box()
    ilocBox = file1.find_iloc_box()

    infeBox47 = file1.find_infe_box(id=47)
    ilocEntry47 = file1.find_iloc_item(id=47)
    #ipmaEntry47 = file.find_impa_entry(id=47)

    newinfebox = copy.deepcopy(infeBox47)
    newilocitem = copy.deepcopy(ilocEntry47)
    #newipmaitem = copy.deepcopy(ipmaEntry47)

    #file1.set_infe_box_id(newinfebox, 54)
    #file1.set_iloc_item_id(newilocitem,54)
    #file1.set_impa_item_id(newipmaitem,54)

    adjust = file1.add_infe_box(newinfebox)
    adjust += file1.add_iloc_item(newilocitem)
    #adjust += file1.add_impa_item(newipmaitem)

    file1.adjust_iloc_item_offsets(adjust)




    file1.save("/home/kali/samples/IMG_3802_test2.HEIC")


