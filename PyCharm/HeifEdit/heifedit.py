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

    MetaBox = file1.findMetaBox()

    ##bytes0 = MetaBox.serialize()

    iinf_Box = file1.find_iinf_Box(MetaBox)

    infe47 = iinf_Box.children[47]

    infe47_copy = copy.deepcopy(infe47)

    file1.add_infe_Box(infe47_copy)

    file1.save("/home/kali/samples/IMG_3802_test2.HEIC")


