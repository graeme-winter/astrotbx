from __future__ import absolute_import, division, print_function

import iotbx.phil

phil_scope = iotbx.phil.parse("""
  raw {
    depth = 16
      .type = int
    demosaic = aahd *ahd linear
      .type = choice
    space = srgb wide adobe *raw
      .type = choice
    channel = *r *g *b
      .type = choice(multi=True)
    convert_xyz = false
      .type = bool
  }
""", process_includes=False)

defaults = phil_scope.extract()

def adobe_rgb_to_xyz(r, g, b):
  '''Convert adobe encoded RGB values to x, y, z linearised values.'''
  from scitbx.array_family import flex

  scale = 1.0 / 255.0
  gamma = 563.0 / 256.0

  rl = flex.pow(r * scale, gamma)
  gl = flex.pow(g * scale, gamma)
  bl = flex.pow(b * scale, gamma)

  # matrix from https://www.adobe.com/digitalimag/pdfs/AdobeRGB1998.pdf
  x = 0.57557 * rl + 0.18556 * gl + 0.18823 * bl
  y = 0.29734 * rl + 0.62736 * gl + 0.07529 * bl
  z = 0.02703 * rl + 0.07069 * gl + 0.99134 * bl

  return x, y, z

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
  _r = int('r' in params.channel)
  _g = int('g' in params.channel)
  _b = int('b' in params.channel)
  return _r * r + _g * g + _b * b

def load_raw_image(image, params=None):
  '''Read as RGB channels, return double array of each i.e. tuple r, g, b.'''
  import numpy
  import rawpy
  from scitbx.array_family import flex

  if params is None:
    params = defaults.raw

  space = {'wide':rawpy.ColorSpace.Wide,
           'srgb':rawpy.ColorSpace.sRGB,
           'adobe':rawpy.ColorSpace.Adobe,
           'raw':rawpy.ColorSpace.raw}
  demosaic = {'ahd':rawpy.DemosaicAlgorithm.AHD,
              'aahd':rawpy.DemosaicAlgorithm.AAHD,
              'linear':rawpy.DemosaicAlgorithm.LINEAR}

  raw = rawpy.imread(image)
  # raw.raw_pattern - pattern of R, G, B, G pixels / map to white
  # raw.camera_whitebalance - scale factors for pixels (filter transmissions?)
  # colours a property too, somewhere
  rgb = raw.postprocess(output_bps=params.depth, use_camera_wb=True,
                        no_auto_scale=False, no_auto_bright=True,
                        demosaic_algorithm=demosaic[params.demosaic],
                        output_color=space[params.space])
  r = flex.double(numpy.double(rgb[:,:,0]))
  g = flex.double(numpy.double(rgb[:,:,1]))
  b = flex.double(numpy.double(rgb[:,:,2]))

  if params.convert_xyz:
    assert params.space == 'adobe'
    return adobe_rgb_to_xyz(r, g, b)
  return r, g, b
