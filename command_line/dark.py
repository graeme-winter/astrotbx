from __future__ import absolute_import, division, print_function

import iotbx.phil

phil_scope = iotbx.phil.parse("""
  min = -32
    .type = float
  max = 32
    .type = float
  bins = 64
    .type = int
  histogram = diff_histogram.png
    .type = path
  log = false
    .type = bool
  output = dark.pickle
    .type = path
  include scope astrotbx.input_output.loader.phil_scope
""", process_includes=True)

def run(args):
  from dials.util.options import OptionParser
  import libtbx.load_env

  usage = "%s [options] DSC0*.ARW" % (
    libtbx.env.dispatcher_name)

  parser = OptionParser(
    usage=usage,
    phil=phil_scope)

  params, options, args = parser.parse_args(show_diff_phil=True,
                                            return_unhandled=True)

  from astrotbx.input_output.loader import load_dark_image
  from scitbx.array_family import flex

  total = None

  # first build up mean dark image

  for arg in args:
    image = load_dark_image(arg)
    if total is None:
      total = image
    else:
      total += image

  dark = total * (1.0 / len(args))

  # then subtract it from each other image and look at residual

  hist = None

  for j, arg in enumerate(args):
    print('Reading %s (%3d/%3d)' % (arg, j+1, len(args)))
    image = load_dark_image(arg)
    diff = (image - dark).as_1d()
    if hist is None:
      hist = flex.histogram(diff, data_min=params.min,
                            data_max=params.max,
                            n_slots=params.bins)
    else:
      temp = flex.histogram(diff, data_min=params.min,
                            data_max=params.max,
                            n_slots=params.bins)
      hist.update(temp)

  # save histogram

  from matplotlib import pyplot

  v = hist.slot_centers().as_double()
  n = hist.slots().as_double()
  pyplot.bar(v, n, log=params.log)
  pyplot.savefig(params.histogram)

if __name__ == '__main__':
  import sys
  import matplotlib
  matplotlib.use('Agg')
  run(sys.argv[1:])
