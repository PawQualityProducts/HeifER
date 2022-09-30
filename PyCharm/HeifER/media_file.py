# -*- coding: utf-8 -*-
from .box import indent
from .box import read_box
import os
from . import output

class MediaFile(object):

    def __init__(self):
        self.ftyp = None
        self.mdats = []
        self.meta = None
        self.moov = None

    def __repr__(self):
        rep = 'ftyp: ' + self.ftyp.__repr__() + '\n'
        rep += 'meta:' + self.meta.__repr__() + '\n'
        rep += 'moov: ' + self.moov.__repr__() + '\n'
        for mdat in self.mdats:
            rep += 'mdat: ' + mdat.__repr__() + '\n'
        return 'ISOBaseMediaFile\n' + indent(rep)

    def read(self, file_name):
        output.open(file_name + '.map')

        file = open(file_name, 'rb')
        try:
            filelength = os.stat(file.name).st_size     # get the length of the file
            setattr(file,'length', filelength)          # add the length attribute and set it to the file length
            print("parsing {0}, size={1}".format(file.name, file.length))
            while file.tell() < file.length:
                box = read_box(file,0)
                if not box:
                    break

                if box.box_type == 'mdat':
                    # appends to local mdat
                    self.mdats.append(box)
                else:
                    # sets local ftyp, meta, mov
                    setattr(self, box.box_type, box)

            summary = self.__repr__()
            output.write(summary)
        finally:
            file.close()
            output.close()


    def extract(self,input_filename,output_filename,start,end):
        outfile = open(output_filename,'wb')
        infile = open(input_filename, 'rb')
        try:
            filelength = os.stat(infile.name).st_size  # get the length of the file
            if (start >= 0) and start < end <= filelength:
                infile.seek(start)
                outfile.write(infile.read(end-start))
        except:
            pass

        finally:
            outfile.close()
            infile.close()

