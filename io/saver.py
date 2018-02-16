from __future__ import absolute_import, division, print_function

def save_image(filename, r, g, b):
  '''Save file to filename with channels r, g, b.'''

  import numpy
  from PIL import Image

  ri = r.iround()
  gi = g.iround()
  bi = b.iround()

  # prevent saturation of pixels > 0xff

  ri.set_selected(ri > 255, 255)
  gi.set_selected(gi > 255, 255)
  bi.set_selected(bi > 255, 255)

  rn = Image.fromarray(numpy.uint8(ri.as_numpy_array()))
  gn = Image.fromarray(numpy.uint8(gi.as_numpy_array()))
  bn = Image.fromarray(numpy.uint8(bi.as_numpy_array()))

  Image.merge('RGB', (rn, gn, bn)).save(filename)
