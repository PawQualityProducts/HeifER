import isobmfflib
import sys
from isobmfflib import log
import os
import io
from PIL import Image
import pyheif
import exifread

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
        log.writeln("ERROR:{0}".format(str(x)))
        print("ERROR:{0}".format(str(x)))


def exportExif(infile,outdir):
    infilename = os.path.basename(infile)
    outfilename = os.path.join(outdir, infilename + ".exif")
    heif_file = pyheif.read(infile)
    outfile = open(outfilename,"w")
    if heif_file.metadata:
        for metadata in heif_file.metadata:
            file_stream = io.BytesIO(metadata['data'][6:])
            tags = exifread.process_file(file_stream,details=False)
            for k,v in tags.items():
                outfile.write("{0}={1}\n".format(k,v))

    outfile.close()


#Entry -------------

log.echo_off()

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
        log.writeln(str(x))
        print("ERROR:{0}".format(str(x)))

    log.writeln("Parse Complete --------")

    log.writeln("")
    log.writeln("Processing Binary Data and Hashes --------------")
    try:
        media_file.ProcessBinaryDataAndHashes()
    except Exception as x:
        log.writeln(str(x))
        print("ERROR:{0}".format(str(x)))

    log.writeln("Binary Data and Hash processing complete -------")

    log.writeln("")
    log.writeln("Writing map file--------------")
    try:
        media_file.mapFile()
    except Exception as x:
        log.writeln(str(x))
        print("ERROR:{0}".format(str(x)))
    log.writeln("map file complete -------")

    log.writeln("")
    log.writeln("Writing contents file--------------")
    try:
        media_file.writeall(infile)
    except Exception as x:
        log.writeln(str(x))
        print("ERROR:{0}".format(str(x)))
    log.writeln("Contents file complete -------")

    log.writeln("Extracting components--------------")
    try:
        media_file.exportAll()
    except Exception as x:
        log.writeln(str(x))
        print("ERROR:{0}".format(str(x)))
    log.writeln("Component Extraction complete-------")

    log.writeln("Extracting metadata--------------")
    try:
        exportExif(infile,outdir)
    except Exception as x:
        log.writeln(str(x))
        print("ERROR:{0}".format(str(x)))
    log.writeln("Metadata extraction complete-------")

    log.writeln("Extracting Images -----------")
    try:
        extractImages(infile,outdir)
    except Exception as x:
        log.writeln(str(x))
        print("ERROR:{0}".format(str(x)))
    log.writeln("Image extraction complete----------")

    log.close()


print(media_file)




