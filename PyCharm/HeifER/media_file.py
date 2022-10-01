# -*- coding: utf-8 -*-
from .box import indent
from .box import read_box
import os
from . import output
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

        #open the map file for output
        output.open(filename + '.map')
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
            output.write(summary)
        except:
            #if not successfully parsed, reset filename and length
            self.filename = None
            self.filelength = 0
        finally:
            infile.close()
            output.close()


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
            start = box.location
            length = box.get_box_size_with_header()

            #get the binary data from the file and calculate the hash
            infile.seek(start)
            box.data = infile.read(length)
            box.hash = hashlib.md5(box.data).hexdigest()

        except Exception as x:
            pass

    def __AddBoxBinaryData(self,infile,box):
        self.__GetBoxBinaryDataFromFile(infile, box)
        for child in box.children:
            self.__AddBoxBinaryData(infile,child)

    def AddBinaryData(self):
        if self.filename != None:
            infile = open(self.filename, 'rb')
            for box in self.children:
                self.__AddBoxBinaryData(infile,box)
        else:
            print("Meadia file must be parsed")

        pass

