from __future__ import absolute_import, division, print_function

def save_image(filename, r, g, b):
  '''Save file to filename with channels r, g, b.'''

  import numpy
  from PIL import Image

  rn = Image.fromarray(numpy.uint8(r.iround().as_numpy_array()))
  gn = Image.fromarray(numpy.uint8(g.iround().as_numpy_array()))
  bn = Image.fromarray(numpy.uint8(b.iround().as_numpy_array()))

  Image.merge('RGB', (rn, gn, bn)).save(filename)
