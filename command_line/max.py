from __future__ import absolute_import, division, print_function

import iotbx.phil

phil_scope = iotbx.phil.parse("""
  scale = 1.0
    .type = float
  output = max.png
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

  max_image_r = None
  max_image_g = None
  max_image_b = None

  from astrotbx.input_output.loader import load_image
  from astrotbx.input_output.saver import save_image

  for image in args:
    r, g, b = load_image(image)

    if max_image_r is None:
      max_image_r = r
    else:
      max_image_r.as_1d().copy_selected((r > max_image_r).iselection(),
                                        r.as_1d())

    if max_image_g is None:
      max_image_g = g
    else:
      max_image_g.as_1d().copy_selected((g > max_image_g).iselection(),
                                        g.as_1d())

    if max_image_b is None:
      max_image_b = b
    else:
      max_image_b.as_1d().copy_selected((b > max_image_b).iselection(),
                                        b.as_1d())

  # output the image

  max_image_r *= params.scale
  max_image_g *= params.scale
  max_image_b *= params.scale

  save_image(params.output, max_image_r, max_image_g, max_image_b)

if __name__ == '__main__':
  import sys
  run(sys.argv[1:])
