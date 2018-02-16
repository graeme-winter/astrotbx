from __future__ import absolute_import, division, print_function

import iotbx.phil

phil_scope = iotbx.phil.parse("""
  scale = 1.0
    .type = float
  output = summed.png
    .type = path
""", process_includes=False)

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

  sum_image_r = None
  sum_image_g = None
  sum_image_b = None

  from astrotbx.io.loader import load_image
  from astrotbx.io.saver import save_image

  for image in args:
    r, g, b = load_image(image)

    if sum_image_r is None:
      sum_image_r = r
    else:
      sum_image_r += r

    if sum_image_g is None:
      sum_image_g = g
    else:
      sum_image_g += g

    if sum_image_b is None:
      sum_image_b = b
    else:
      sum_image_b += b

  # output the image

  sum_image_r *= params.scale / len(args)
  sum_image_g *= params.scale / len(args)
  sum_image_b *= params.scale / len(args)

  save_image(params.output, sum_image_r, sum_image_g, sum_image_b)

if __name__ == '__main__':
  import sys
  run(sys.argv[1:])
