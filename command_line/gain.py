from __future__ import absolute_import, division, print_function

import iotbx.phil

phil_scope = iotbx.phil.parse("""
  min = 0
    .type = float
  max = 100
    .type = float
  slots = 1000
    .type = int
  output = gain.png
    .type = path
  include scope astrotbx.input_output.loader.phil_scope
""", process_includes=True)

def gain(image, params):
  from dials.algorithms.image import filter
  from astrotbx.input_output.loader import load_image_gs, load_raw_image_gs
  from dials.array_family import flex
  from matplotlib import pyplot

  raws = ['arw']
  exten = image.split('.')[-1].lower()
  if exten in raws:
    image = load_raw_image_gs(image, params.raw)
  else:
    image = load_image_gs(image)

  disp = filter.index_of_dispersion_filter(image, (3, 3)).index_of_dispersion()
  hist = flex.histogram(disp.as_1d(), data_min=params.min, data_max=params.max,
                        n_slots=params.slots)

  v = hist.slot_centers().as_double()
  n = hist.slots().as_double()
  fix, axes = pyplot.subplots()
  pyplot.bar(v, n)
  axes.set_xlabel('variance / mean')
  pyplot.savefig(params.output)

  return

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

  gain(args[0], params)

if __name__ == '__main__':
  import sys
  import matplotlib
  matplotlib.use('Agg')
  run(sys.argv[1:])
