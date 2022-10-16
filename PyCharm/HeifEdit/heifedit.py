import copy
import heiffile

class HeifEditor(object):
    def __init__(self):
        pass

#-----------


if __name__ == '__main__':
    file1 = heiffile.HeifFile()
    file1.load("/home/kali/samples/IMG_3802b.HEIC")
    file1.save("/home/kali/samples/processed/IMG_3802_test.HEIC")

    MetaBox = file1.find_meta_box()

    ##bytes0 = MetaBox.serialize()

    iinfBox = file1.find_iinf_box(MetaBox)

    infe47Box = iinfBox.children[47]

    infe47BoxCopy = copy.deepcopy(infe47Box)

    file1.add_infe_Box(infe47BoxCopy)

    file1.save("/home/kali/samples/processed/IMG_3802_test2.HEIC")


