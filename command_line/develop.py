from __future__ import absolute_import, division, print_function

import iotbx.phil

phil_scope = iotbx.phil.parse("""
  scale = 1.0
    .type = float
  output = developed.png
    .type = path
  data = stacked.pickle
    .type = path
  include scope astrotbx.input_output.saver.phil_scope
""", process_includes=True)

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

  import cPickle as pickle
  from dials.array_family import flex

  with open(params.data) as fin:
    sum_image_r, sum_image_g, sum_image_b = pickle.load(fin)

  sum_image_r *= params.scale
  sum_image_g *= params.scale
  sum_image_b *= params.scale

  # output the image

  from astrotbx.input_output.saver import save_image
  save_image(params.output, sum_image_r, sum_image_g, sum_image_b, params.png)

if __name__ == '__main__':
  import sys
  run(sys.argv[1:])
