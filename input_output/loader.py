from __future__ import absolute_import, division, print_function

import iotbx.phil

phil_scope = iotbx.phil.parse("""
  raw {
    depth = 16
      .type = int
    demosaic = *aahd ahd
      .type = choice
    space = *srgb wide adobe
      .type = choice
  }
""", process_includes=False)

defaults = phil_scope.extract()

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

def load_raw_image_gs(image, params=None):
  r, g, b = load_raw_image(image, params)
  return r + g + b

def load_raw_image(image, params=None):
  '''Read as RGB channels, return double array of each i.e. tuple r, g, b.'''
  import numpy
  import rawpy
  from scitbx.array_family import flex

  if params is None:
    params = defaults.raw

  space = {'wide':rawpy.ColorSpace.Wide,
           'srgb':rawpy.ColorSpace.sRGB,
           'adobe':rawpy.ColorSpace.Adobe}
  demosaic = {'ahd':rawpy.DemosaicAlgorithm.AHD,
              'aahd':rawpy.DemosaicAlgorithm.AAHD}

  raw = rawpy.imread(image)
  rgb = raw.postprocess(output_bps=params.depth, no_auto_scale=True,
                        demosaic_algorithm=demosaic[params.demosaic],
                        output_color=space[params.space],
                        no_auto_bright=True, use_camera_wb=False)
  r = flex.double(numpy.double(rgb[:,:,0]))
  g = flex.double(numpy.double(rgb[:,:,1]))
  b = flex.double(numpy.double(rgb[:,:,2]))

  return r, g, b
