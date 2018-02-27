from __future__ import division, print_function

import iotbx.phil

phil_scope = iotbx.phil.parse("""
  output = histogram.png
    .type = path
  log_n = false
    .type = bool
""", process_includes=False)

def gs_histogram(params, image):
  from astrotbx.input_output.loader import load_image_gs
  from dials.array_family import flex
  from matplotlib import pyplot
  data = load_image_gs(image)
  dmax = flex.max(data)

  pixels = flex.histogram(data.as_1d(), data_min=0, data_max=dmax,
                          n_slots=int(dmax))
  v = pixels.slot_centers().as_double()
  n = pixels.slots().as_double()
  pyplot.bar(v, n, log=params.log_n)
  pyplot.savefig(params.output)

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

  gs_histogram(params, args[0])

if __name__ == '__main__':
  import sys
  import matplotlib
  matplotlib.use('Agg')
  run(sys.argv[1:])
