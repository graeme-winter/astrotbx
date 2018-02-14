from PIL import Image
import sys
import numpy

scale = 1 * (1.0 / len(sys.argv[1:]))

sum_image = None
for arg in sys.argv[1:]:
  print(arg)
  image = Image.open(arg)
  n_image = scale * numpy.asarray(image)
  if sum_image is None:
    sum_image = n_image
  else:
    sum_image = sum_image + n_image

image = Image.fromarray(numpy.uint8(sum_image))
image.save('stacked.png')
