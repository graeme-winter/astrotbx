from __future__ import division, print_function

import iotbx.phil

phil_scope = iotbx.phil.parse("""
  output = histogram_%s.png
    .type = path
  log_n = false
    .type = bool
  colour = *r g b
    .type = choice
""", process_includes=False)

def loader(image):
  import numpy
  import rawpy
  from scitbx.array_family import flex

  raw = rawpy.imread(image)
  rgb = raw.postprocess(output_bps=16, no_auto_scale=True,
                        output_color=rawpy.ColorSpace.Wide,
                        no_auto_bright=True, use_camera_wb=True)
  r = flex.double(numpy.double(rgb[:,:,0]))
  g = flex.double(numpy.double(rgb[:,:,1]))
  b = flex.double(numpy.double(rgb[:,:,2]))

  # try to work out the true ADU scale

  min_r = flex.min(r.as_1d().select(r.as_1d() > 0))
  min_g = flex.min(g.as_1d().select(g.as_1d() > 0))
  min_b = flex.min(b.as_1d().select(b.as_1d() > 0))

  adu = min(min_r, min_g, min_b)

  return r / adu, g / adu, b / adu

def histogram(params, image):
  from dials.array_family import flex
  from matplotlib import pyplot
  r, g, b = loader(image)
  dmax = max(flex.max(r), flex.max(g), flex.max(b))

  if params.colour == 'r':
    data = r
  elif params.colour == 'g':
    data = g
  else:
    data = b

  pixels = flex.histogram(data.as_1d(), data_min=0, data_max=dmax,
                          n_slots=int(dmax))
  v = pixels.slot_centers().as_double()
  n = pixels.slots().as_double()
  pyplot.bar(v, n, log=params.log_n)
  pyplot.savefig(params.output % params.colour)

def run(args):
  from dials.util.options import OptionParser
  import libtbx.load_env
  import json

  usage = "%s [options] DSC03206.jpg" % (
    libtbx.env.dispatcher_name)

  parser = OptionParser(
    usage=usage,
    phil=phil_scope)

  params, options, args = parser.parse_args(show_diff_phil=True,
                                            return_unhandled=True)

  histogram(params, args[0])

if __name__ == '__main__':
  import sys
  import matplotlib
  matplotlib.use('Agg')
  run(sys.argv[1:])
