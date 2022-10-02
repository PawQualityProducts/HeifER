from PIL import Image
import pyheif

heif_file = pyheif.read("HeifER/samples/IMG_3802.HEIC")
image = Image.frombytes(
    heif_file.mode,
    heif_file.size,
    heif_file.data,
    "raw",
    heif_file.mode,
    heif_file.stride,
    )

image.save("IMG_7424.jpg", "JPEG")

