from PIL import Image
import pyheif
import os

def saveImage(heif_file,outfilename):
    image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )
    image.save(outfilename, "JPEG")

def extractImages(infile):
    try:
        infilename = os.path.basename(infile)

        #easy get primary image
        heif_file = pyheif.read(infile)
        saveImage(heif_file,infilename + "_primary1")

        container = pyheif.open_container(infile)
        heif_file = container.primary_image.image.load()
        saveImage(heif_file,infilename + "_primary2")

        index=0
        for img in container.top_level_images:
            heif_file = img.image.load()
            saveImage(heif_file, "{0}_top_level_{1}_primary_{2}_{3}.jpg".format(infilename, img.id,img.is_primary,str(index).zfill(3)))


            metadata = heif_file.metadata
            if metadata:
                pass        #todo: add exif processing here

            if img.depth_image:
                depth_heif = img.depth_image.image.load()
                saveImage(depth_heif,"{0}_depth_{0}.jpg".format(infilename,str(index).zfill(3)))

            auxIndex = 1
            for auximg in img.auxiliary_images:
                aux_heif = auximg.image.load()
                saveImage(aux_heif,"{0}_aux_id_{1}_type_{2}_{3}_{4}.jpg".format(infilename,auximg.id,auximg.type,str(index).zfill(3), str(auxIndex).zfill(3)))
                auxIndex += 1

            index += 1

    except Exception as x:
        print(str(x))


#extractImages("/home/kali/samples/IMG_3802.HEIC")
#extractImages("/home/kali/samples/bothie_1440x960.heic")
#extractImages("/home/kali/samples/cheers_1440x960.heic")
#extractImages("/home/kali/samples/grid_960x640.heic")
extractImages("/home/kali/samples/rally_burst.heic")

