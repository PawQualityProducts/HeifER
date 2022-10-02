# -*- coding: utf-8 -*-
from .box import indent
from .box import read_box
import os
from . import log
import hashlib

class MediaFile(object):

    def __init__(self):
        self.ftyp = None
        self.mdats = []
        self.meta = None
        self.moov = None
        self.children = []
        self.filename = None
        self.filelength = 0;

    def __repr__(self):
        rep = 'ftyp: ' + self.ftyp.__repr__() + '\n'
        rep += 'meta:' + self.meta.__repr__() + '\n'
        rep += 'moov: ' + self.moov.__repr__() + '\n'
        for mdat in self.mdats:
            rep += 'mdat: ' + mdat.__repr__() + '\n'
        return 'ISOBaseMediaFile\n' + indent(rep)

    def read(self, filename):
        self.filename = filename
        self.filelength = os.stat(filename).st_size  # get the length of the file

        infile = open(filename, 'rb')
        try:
            setattr(infile,'length', self.filelength)          # add the length attribute and set it to the file length
            print("parsing {0}, size={1}".format(self.filename, self.filelength))
            while infile.tell() < infile.length:
                box = read_box(infile,0)
                if not box:
                    break

                if box.box_type == 'mdat':
                    # appends to local mdat
                    self.mdats.append(box)
                    self.children.append(box)
                else:
                    # sets local ftyp, meta, mov
                    setattr(self, box.box_type, box)
                    self.children.append(box)

            summary = self.__repr__()
            log.writeln(summary)
        except Exception as x:
            #if not successfully parsed, reset filename and length
            self.filename = None
            self.filelength = 0
            log.writeln(x)
        finally:
            infile.close()

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
            pass

        finally:
            outfile.close()
            infile.close()


    def __GetBoxBinaryDataFromFile(self,infile,box):
        try:
            start = box.startByte
            length = box.get_box_size_with_header()

            #get the binary data from the file and calculate the hash
            infile.seek(start)
            box.data = infile.read(length)
            box.hash = hashlib.md5(box.data).hexdigest()

            log.writeln("{0}:{1}{2} Hash={3}".format(str(start).rjust(6), "-" * box.depth, box.box_type, box.hash))
            #log.writeln("{0}{1}:{2}{3} Hash={4}".format(" " * 6,box.location,"-" * box.depth, box.box_type, box.hash))
        except Exception as x:
            log.writeln(str(x))
            print(str(x))
            pass

    def __AddBoxBinaryData(self,infile,box):
        self.__GetBoxBinaryDataFromFile(infile, box)
        for child in box.children:
            self.__AddBoxBinaryData(infile,child)

    def ProcessBinaryDataAndHashes(self):
        if self.filename != None:
            infile = open(self.filename, 'rb')
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
        outfile = open(filename + ".txt",'w')
        for box in self.children:
            self.__write(outfile,box,0,True,False)
        log.writeln("write all complete")
        outfile.close()


    def __exportBox(self,box,parentdir,index=0):
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
        index = 0
        for child in box.children:
            self.__exportBox(child,boxdir,index)
            index += 1

    def exportAll(self,parentdir):
        filepath = os.path.join(parentdir, self.filename + ".export")
        os.makedirs(filepath)
        print(parentdir)
        print(filepath)
        filename = os.path.join(filepath,self.filename + ".txt")
        outfile = open(filename,"w")
        outfile.write("Export {0}\n".format(filename))
        outfile.close()
        for child in self.children:
            self.__exportBox(child,filepath)

