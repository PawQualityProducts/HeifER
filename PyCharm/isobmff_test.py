import isobmff

media_file = isobmff.MediaFile()
media_file.read('IMG_3802.HEIC')
print(media_file)
