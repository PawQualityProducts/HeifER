# HeifER
Heif ER, a prototype forensic analysis tool for HEIF files

HEIF is a relatively new image file format implementing modern features such as an efficient compression algorithm offering significant improvements over JPEG.
But, it is far more than a single-image file format. It is a media-container capable of holding multiple images, video and other types of media, and could potentially be used to distribute illegal content. Detailed analysis of HEIF files is therefore essential during a forensic investigation, however they have a complex structure and analysis can be a complicated, time-consuming and error-prone task.

PQ HeifER  (Heif Emergency Room) is a tool designed specifically to assist the digital forensics investigator in the detailed analysis of HEIF image files.

It parses HEIF files creating a "Map" of the file structure, extracting all images, metadata and  other details from the file that may be useful during a forensic investigation. During processing, a directory structure is created containing human-readable and binary content extracted from the file ready for analysis.

## References
* This tool is built upon the base [ISOBMFF Library](https://github.com/m-hiki/isobmff) created by Hiki.  
* [ISO/IEC 14496-12:2015 ISO Base Media File Format](http://mpeg.chiariglione.org/standards/mpeg-4/iso-base-media-file-format/text-isoiec-14496-12-5th-edition)  
* [ISO/IEC CD 23008-12 HEVC Still Image File Format](http://mpeg.chiariglione.org/standards/mpeg-h/image-file-format/text-isoiec-cd-23008-12-image-file-format)  
