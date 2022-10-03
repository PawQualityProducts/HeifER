import isobmfflib
import sys
from isobmfflib import log
import os
from PIL import Image
import pyheif

arg_infile = sys.argv[1]             #input heif file, next arg is infile name
arg_outdir = sys.argv.index('-outdir')  if '-outdir' in sys.argv[2:] else 0  #destination directory
arg_map = sys.argv.index('-map')  if '-map' in sys.argv[2:] else 0              #output map file, next arg is output file name
arg_extract_binary = sys.argv.index('-exb') if '-exb' in sys.argv[2:] else 0    #extract binary, next arg is output filename
arg_extract_text = sys.argv.index('-ext') if '-ext' in sys.argv[2:] else 0      #extract text, next arg is output filename
arg_from = sys.argv.index('-start') if '-start' in sys.argv[2:] else 0          #extract start byte
arg_to = sys.argv.index('-end') if '-end' in sys.argv[2:] else 0                #extract end byte
arg_meta = sys.argv.index('-exm') if '-exm' in sys.argv[2:] else 0              #extract metadata metadata
arg_images = sys.argv.index('-exi') if '-exi' in sys.argv[2:] else 0            #extract images
arg_help = sys.argv.index('-h') if '-h' in sys.argv[1:] else 0                  #help
arg_echo = sys.argv.index('-echo') if '-echo' in sys.argv[2:] else 0            #echo on|off
arg_extract_auto = sys.argv.index('-exa') if '-exa' in sys.argv[2:] else 0      #extract auto

media_file = isobmfflib.MediaFile()

def parseExtractArgs(extractIndex):
    if len(sys.argv) > extractIndex + 3:
        if sys.argv[extractIndex+1][0] != '-' and sys.argv[extractIndex+2].isnumeric() and sys.argv[extractIndex+3].isnumeric():
            return sys.argv[extractIndex+1], int(sys.argv[extractIndex+2]), int(sys.argv[extractIndex+3])
        else:
            raise ValueError('Format : {0} type start end'.format(sys.argv[extractIndex]))
    else:
        raise ValueError('Format : {0} type start end'.format(sys.argv[extractIndex]))

# HeifLib ------------

def __saveImage(heif_file,outfilename):
    image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )
    image.save(outfilename, "JPEG")

def extractImages(infile,outdir):
    try:
        infilename = os.path.basename(infile)

        #easy get primary image
        #heif_file = pyheif.read(infile)
        #saveImage(heif_file,infilename + "_primary1")

        container = pyheif.open_container(infile)
        heif_file = container.primary_image.image.load()
        outfilename = "{0}_primary".format(os.path.join(outdir, infilename))
        __saveImage(heif_file,outfilename)

        index=0
        for img in container.top_level_images:
            index += 1
            heif_file = img.image.load()

            outfilename =  "{0}_id_{1}_primary_{2}.jpg".format(os.path.join(outdir, str(index).zfill(3)), img.id,img.is_primary)
            __saveImage(heif_file, outfilename)

            metadata = heif_file.metadata
            if metadata:
                pass        #todo: add exif processing here

            if img.depth_image:
                index+=1
                depth_heif = img.depth_image.image.load()
                outfilename = "{0}_id_{1}_depthmap.jpg".format(os.path.join(outdir, str(index).zfill(3)))
                __saveImage(depth_heif,outfilename)

            for auximg in img.auxiliary_images:
                index += 1
                aux_heif = auximg.image.load()
                outfilename = "{0}_aux_id_{1}_type_{2}".format(os.path.join(outdir, str(index).zfill(3)),auximg.id,auximg.type)
                __saveImage(aux_heif,outfilename)

    except Exception as x:
        print(str(x))
        log.writeln("ERROR:" + str(x))


#Entry -------------

if arg_infile and arg_infile[0] != '-':

    infile = arg_infile

    if arg_outdir:
        outdir = sys.argv[arg_outdir + 1]

        try:
            os.makedirs(outdir)
        except Exception as x:
            print("ERROR:{0}".format(str(x)))
    else:
        outdir = os.path.dirname(infile)

    infilename = os.path.basename(infile)
    log.open(os.path.join(outdir,infilename +".log"))

    log.writeln("Parsing file ------------")
    try:
        media_file.read(infile,outdir)
    except Exception as x:
        print("ERROR:{0}".format(str(x)))

    log.writeln("Parse Complete --------")

    log.writeln("")
    log.writeln("Processing Binary Data and Hashes --------------")
    try:
        media_file.ProcessBinaryDataAndHashes()
    except Exception as x:
        print("ERROR:{0}".format(str(x)))

    log.writeln("Binary Data and Hash processing complete -------")

    log.writeln("")
    log.writeln("Writing map file--------------")
    try:
        media_file.mapFile()
    except Exception as x:
        print("ERROR:{0}".format(str(x)))
    log.writeln("map file complete -------")

    log.writeln("")
    log.writeln("Writing contents file--------------")
    try:
        media_file.writeall(infile)
    except Exception as x:
        print("ERROR:{0}".format(str(x)))
    log.writeln("Contents file complete -------")

    log.writeln("Extracting components--------------")
    try:
        media_file.exportAll()
    except Exception as x:
        print("ERROR:{0}".format(str(x)))
    log.writeln("Component Extraction complete-------")

    log.writeln("Extracting images--------------")
    try:
        media_file.exportImage()
    except Exception as x:
        print("ERROR:{0}".format(str(x)))
    log.writeln("Image Extraction complete-------")

    log.writeln("Extracting metadata--------------")
    try:
        media_file.exportExif()
    except Exception as x:
        print("ERROR:{0}".format(str(x)))
    log.writeln("Metadata extraction complete-------")

    log.writeln("Extracting Images -----------")
    try:
        extractImages(infile,outdir)
    except Exception as x:
        log.writeln(str(x))
        print(str(x))
    log.writeln("Image extraction complete----------")

    log.close()

    if arg_extract_binary > 0:
        extype,exstart,exend = parseExtractArgs(arg_extract_binary)
        outfile = infile + '.' + extype + '.bin'
        media_file.extract(infile,outfile,exstart,exend,hash)

    if arg_extract_text > 0:
        extype,exstart,exend = parseExtractArgs(arg_extract_text)
        outfile = infile + '.' + extype + '.txt'
        media_file.extract(infile,outfile,exstart,exend,hash)




#media_file.read('IMG_3802.HEIC') #ok
#media_file.extract('IMG_3802.HEIC','IMG_3802_ftyp.bin',0,40)
#media_file.extract('IMG_3802.HEIC','IMG_3802_meta.bin',40,3737)


#Nokia sample files
#media_file.read('C001.heic')                           #ok
#media_file.read('bothie_1440x960.heic')                #ok
#media_file.read('cheers_1440x960.heic')                #ok
#media_file.read('crowd_1440x960.heic')                 #ok
#media_file.read('grid_960x640.heic')                   #ok
#media_file.read('grid_960x640.heic')                   #ok
#media_file.read('lights_1440x960.heic')                #ok
#media_file.read('old_bridge_1440x960.heic')            #ok
#media_file.read('overlay_1000x680.heic')               #ok
#media_file.read('rally_burst.heic')                    #ok
#media_file.read('random_collection_1440x960.heic')     #ok
#media_file.read('sea1_animation.heic')                 #ok
#media_file.read('season_collection_1440x960.heic')     #ok
#media_file.read('ski_jump_1440x960.heic')              #ok
#media_file.read('spring_1440x960.heic')                #ok
#media_file.read('starfield_animation.heic')            #ok
#media_file.read('stereo_1200x800.heic')                #ok
#media_file.read('summer_1440x960.heic')                #ok
#media_file.read('surfer_1440x960.heic')                #ok
#media_file.read('winter_1440x960.heic')                #ok

print(media_file)




