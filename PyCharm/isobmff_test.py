import isobmff

media_file = isobmff.MediaFile()
media_file.read('IMG_3802.HEIC')
#media_file.read('C001.heic')
print(media_file)


