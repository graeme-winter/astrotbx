from __future__ import absolute_import, division, print_function

import iotbx.phil

phil_scope = iotbx.phil.parse("""
  raw = False
    .type = bool
""", process_includes=False)

def run(args):
  from dials.util.options import OptionParser
  import libtbx.load_env

  usage = "%s [options] DSC03206.jpg" % (
    libtbx.env.dispatcher_name)

  parser = OptionParser(
    usage=usage,
    phil=phil_scope)

  params, options, args = parser.parse_args(show_diff_phil=True,
                                            return_unhandled=True)

  from astrotbx.input_output.loader import load_image, load_raw_image
  from dials.array_family import flex

  for j, arg in enumerate(args):
    if params.raw:
      r, g, b = load_raw_image(arg)
    else:
      r, g, b = load_image(arg)
    max_r, max_g, max_b = flex.max(r), flex.max(g), flex.max(b)
    max_pixel = max(max_r, max_g, max_b)

    print(arg, max_pixel, (r >= max_pixel).count(True),
          (g >= max_pixel).count(True), (b >= max_pixel).count(True))

if __name__ == '__main__':
  import sys
  run(sys.argv[1:])
