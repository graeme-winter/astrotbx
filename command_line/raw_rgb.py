from __future__ import division, print_function

import iotbx.phil

phil_scope = iotbx.phil.parse("""
  output = histogram_%s.png
    .type = path
  log_n = false
    .type = bool
  min = 0
    .type = float
  max = 255
    .type = float
  bins = 255
    .type = int
  colour = *r g b
    .type = choice
  save = None
    .type = path
  scale = 1
    .type = float
  include scope astrotbx.input_output.loader.phil_scope
""", process_includes=True)

def histogram(params, image):
  from dials.array_family import flex
  from matplotlib import pyplot
  from astrotbx.input_output.loader import load_raw_image
  r, g, b = load_raw_image(image, params=params.raw)

  r *= params.scale
  g *= params.scale
  b *= params.scale

  dmax = max(flex.max(r), flex.max(g), flex.max(b))

  if params.colour == 'r':
    data = r
  elif params.colour == 'g':
    data = g
  else:
    data = b

  print("Mean / max r: %6.2f / %6.2f" % (flex.mean(r), flex.max(r)))
  print("Mean / max g: %6.2f / %6.2f" % (flex.mean(g), flex.max(g)))
  print("Mean / max b: %6.2f / %6.2f" % (flex.mean(b), flex.max(b)))

  pixels = flex.histogram(data.as_1d(), data_min=params.min,
                          data_max=params.max, n_slots=params.bins)
  v = pixels.slot_centers().as_double()
  n = pixels.slots().as_double()
  pyplot.bar(v, n, log=params.log_n)
  pyplot.savefig(params.output % params.colour)

  if params.save:
    from astrotbx.input_output.saver import save_image
    save_image(params.save, r, g, b)

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
