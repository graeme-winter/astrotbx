from __future__ import absolute_import, division, print_function

def load_image_gs(image):
  '''Load image as RGB channels, convert to float, sum then return flex
  array.'''

  import numpy
  from PIL import Image
  from scitbx.array_family import flex

  r, g, b = map(numpy.asarray, Image.open(image).split())
  gs = numpy.double(r) + numpy.double(g) + numpy.double(b)
  gsd = flex.double(gs)

  return gsd

def load_image(image):
  '''Read as RGB channels, return double array of each i.e. tuple r, g, b.'''

  import numpy
  from PIL import Image
  from scitbx.array_family import flex

  r, g, b = map(numpy.double, map(numpy.asarray, Image.open(image).split()))

  return flex.double(r), flex.double(g), flex.double(b)

def load_raw_image(image):
  '''Read as RGB channels, return double array of each i.e. tuple r, g, b.'''
  import numpy
  import rawpy
  from scitbx.array_family import flex

  raw = rawpy.imread(image)
  rgb = raw.postprocess(output_bps=16, no_auto_scale=True,
                        no_auto_bright=True, use_camera_wb=True)
  r = flex.double(numpy.double(rgb[:,:,0]))
  g = flex.double(numpy.double(rgb[:,:,1]))
  b = flex.double(numpy.double(rgb[:,:,2]))

  return r, g, b

