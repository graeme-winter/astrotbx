from __future__ import absolute_import, division, print_function

import iotbx.phil

phil_scope = iotbx.phil.parse("""
  png {
    negative = false
      .type = bool
  }
""", process_includes=False)

defaults = phil_scope.extract()

def save_image_gs(filename, gs):
  '''Save greyscale image.'''

  import numpy
  from PIL import Image

  gsi = gs.iround()

  # prevent saturation of pixels > 0xff and underloads < 0

  gsi.set_selected(gsi > 255, 255)
  gsi.set_selected(gsi < 0, 0)

  Image.fromarray(numpy.uint8(gsi.as_numpy_array())).save(filename)

def save_image(filename, r, g, b, params=None):
  '''Save file to filename with channels r, g, b.'''

  import numpy
  from PIL import Image

  if params is None:
    params = defaults.png

  ri = r.iround()
  gi = g.iround()
  bi = b.iround()

  # prevent saturation of pixels > 0xff and underloads < 0

  ri.set_selected(ri > 255, 255)
  gi.set_selected(gi > 255, 255)
  bi.set_selected(bi > 255, 255)

  ri.set_selected(ri < 0, 0)
  gi.set_selected(gi < 0, 0)
  bi.set_selected(bi < 0, 0)

  if params.negative:
    ri = ri * -1 + 255
    gi = gi * -1 + 255
    bi = bi * -1 + 255

  rn = Image.fromarray(numpy.uint8(ri.as_numpy_array()))
  gn = Image.fromarray(numpy.uint8(gi.as_numpy_array()))
  bn = Image.fromarray(numpy.uint8(bi.as_numpy_array()))

  Image.merge('RGB', (rn, gn, bn)).save(filename)
