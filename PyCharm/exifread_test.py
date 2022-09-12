import io
import pyheif
import exifread

heif_file = pyheif.read('IMG_3802.HEIC')

for metadata in heif_file.metadata:
  file_stream = io.BytesIO(metadata['data'][6:])
  tags = exifread.process_file(file_stream,details=False)
  for k,v in tags.items():
    print(k,v)

