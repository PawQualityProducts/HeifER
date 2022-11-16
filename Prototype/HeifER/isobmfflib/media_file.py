# -*- coding: utf-8 -*-
from .box import indent
from .box import read_box
import os
from . import log
import hashlib
from . import iloc

import linecache
import sys

def LogException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    log.writeln('***')
    log.writeln('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
    log.writeln('***')


class MediaFile(object):

    def __init__(self):
        self.hash = None
        self.ftyp = None
        self.mdats = []
        self.meta = None
        self.moov = None
        self.children = []
        self.path = None
        self.filename = None
        self.filelength = 0;

    def __repr__(self):
        rep = 'ftyp: ' + self.ftyp.__repr__() + '\n'
        rep += 'meta:' + self.meta.__repr__() + '\n'
        rep += 'moov: ' + self.moov.__repr__() + '\n'
        for mdat in self.mdats:
            rep += 'mdat: ' + mdat.__repr__() + '\n'
        return 'ISOBaseMediaFile\n' + indent(rep)

    def read(self, filepath, outdir=None):
        self.path = os.path.dirname(filepath)
        self.filename = os.path.basename(filepath)
        self.filelength = os.stat(filepath).st_size  # get the length of the file
        if outdir:
            self.outdir = outdir
        else:
            self.outdir = self.path

        infile = open(filepath, 'rb')
        try:
            setattr(infile,'length', self.filelength)          # add the length attribute and set it to the file length
            print("parsing {0}, size={1}".format(self.filename, self.filelength))
            while infile.tell() < infile.length:
                box = read_box(infile,0)
                if box:
                    if box.box_type == 'mdat':
                        # appends to local mdat
                        self.mdats.append(box)
                        self.children.append(box)
                    else:
                        # sets local ftyp, meta, mov
                        setattr(self, box.box_type, box)
                        self.children.append(box)
                else:
                    pass

            summary = self.__repr__()
            log.writeln(summary)
        except Exception as x:
            #if not successfully parsed, reset filename and length
            self.filename = None
            self.filelength = 0
            log.writeln(x)
            LogException()
        finally:
            infile.close()

            #iloc needs the meta box because it contains the idat box
            if hasattr(self,"meta"):
                iloc.setMetaBox(self.meta)


    def extract(self,input_filename,output_filename,start,end,hash=False):
        outfile = open(output_filename,'wb')
        infile = open(input_filename, 'rb')
        try:
            filelength = os.stat(infile.name).st_size  # get the length of the file
            if (start >= 0) and start < end <= filelength:
                infile.seek(start)
                data = infile.read(end-start)
                outfile.write(data)

                if hash:
                    outhashfile = open(output_filename + '.hash','wt')
                    hashResult = hashlib.md5(data).hexdigest()
                    outhashfile.write(hashResult)
                    outhashfile.close()
        except:
            LogException()

        finally:
            outfile.close()
            infile.close()


    def __GetBoxBinaryDataFromFile(self,infile,box):
        try:
            box.getBinaryDataFromFile(infile)
        except Exception as x:
            log.writeln(str(x))
            #print(str(x))
            LogException()


    def __AddBoxBinaryData(self,infile,box):
        self.__GetBoxBinaryDataFromFile(infile, box)
        for child in box.children:
            self.__AddBoxBinaryData(infile,child)

    def ProcessBinaryDataAndHashes(self):
        filepath = os.path.join(self.path,self.filename)
        if self.filename != None:
            infile = open(filepath, 'rb')
            #hash the whole file
            data = infile.read()
            self.hash = hashlib.md5(data).hexdigest()

            #hash the boxes
            infile.seek(0)
            for box in self.children:
                self.__AddBoxBinaryData(infile,box)
        else:
            print("Meadia file must be parsed")
        pass


    def __write(self,outfile,box,depth,writeText,writeData):
        box.write(outfile,depth,writeText=writeText,writeData=writeData,recurse=False)
        for childBox in box.children:
            self.__write(outfile,childBox,depth+1,writeText,writeData)

    def writeall(self, filename):
        log.writeln("write all to {0}".format(filename + ".txt"))
        outfilepath = os.path.join(self.outdir,self.filename + ".txt")
        outfile = open(outfilepath,'w')
        for box in self.children:
            self.__write(outfile,box,0,True,False)
        log.writeln("write all complete")
        outfile.close()


    def __exportBox(self,box,parentdir,index=1):
        boxdir = os.path.join(parentdir, str(index).zfill(3) + "_" + box.box_type)
        os.makedirs(boxdir)
        txtfilename = os.path.join(boxdir,str(index).zfill(3) + "_" + box.box_type + ".txt")
        outfile = open(txtfilename,"w")
        box.writeText(outfile,0)
        outfile.close
        datafilename = os.path.join(boxdir,str(index).zfill(3) + "_" + box.box_type + ".bin")
        outfile = open(datafilename,"wb")
        box.writeData(outfile)
        outfile.close()
        index=1
        for child in box.children:
            self.__exportBox(child,boxdir,index)
            index += 1

    def exportAll(self):
        #filename = os.path.join(self.outdir,self.filename + ".txt")
        #outfile = open(filename,"w")
        #outfile.write("Export {0}\n".format(filename))
        #self.__mapFile(outfile)
        #outfile.close()
        index = 1
        for child in self.children:
            self.__exportBox(child,self.outdir,index)
            index += 1


    def __mapFile(self,file):
        for box in self.children:
            box.writeMapEntry(file,0)

    def mapFile(self):
        filepath = os.path.join(self.outdir, self.filename + ".map")

        outfile = open(filepath,"w")

        outfile.write("File={0}, hash={1}\n".format(self.filename,self.hash))
        self.__mapFile(outfile)

        outfile.close()

    def __findBoxes(self,boxType,box,boxes):
        if box.box_type == boxType:
            boxes.append(box)

        for childBox in box.children:
            self.__findBoxes(boxType,childBox,boxes)


    def findBoxes(self,boxType):
        boxes = []
        for box in self.children:
            self.__findBoxes(boxType,box,boxes)
        return boxes

    def findExifLocItems(self):
        irefBoxes = self.findBoxes('infe')
        exifItemIds = []
        for irefbox in irefBoxes:
            if irefbox.item_type == 'Exif':
                exifItemIds.append(irefbox.item_id)

        ilocBoxes = self.findBoxes('iloc')
        items = []
        for box in ilocBoxes:
            for item in box.items:
                if item['item_id'] in exifItemIds:
                    items.append(item)
        return items


