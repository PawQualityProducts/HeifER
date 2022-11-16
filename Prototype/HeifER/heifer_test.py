import isobmfflib
import sys
from isobmfflib import log
import os

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

class HeifFile():
    pass

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




