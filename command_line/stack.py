from __future__ import absolute_import, division, print_function

import iotbx.phil

phil_scope = iotbx.phil.parse("""
  alignments = rotations.json
    .type = path
  scale = 1.0
    .type = float
  output = stacked.png
    .type = path
  greyscale = false
    .type = bool
  include scope astrotbx.input_output.loader.phil_scope
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

  Rtds = json.load(open(params.alignments))
  assert len(Rtds) == len(args)

  sum_image_r = None
  sum_image_g = None
  sum_image_b = None

  from astrotbx.input_output.loader import load_image, load_raw_image
  from astrotbx.input_output.saver import save_image, save_image_gs
  from astrotbx.algorithms.image_align import rotate_translate_array

  raws = ['arw']

  for image, alignment in zip(args, Rtds):
    print("Loading %s" % image)
    R, t = alignment['R'], alignment['t']
    exten = image.split('.')[-1].lower()
    if exten in raws:
      r, g, b = load_raw_image(image, params.raw)
    else:
      r, g, b = load_image(image)

    _r = rotate_translate_array(r, R, t)
    _g = rotate_translate_array(g, R, t)
    _b = rotate_translate_array(b, R, t)

    if sum_image_r is None:
      sum_image_r = _r
    else:
      sum_image_r += _r

    if sum_image_g is None:
      sum_image_g = _g
    else:
      sum_image_g += _g

    if sum_image_b is None:
      sum_image_b = _b
    else:
      sum_image_b += _b

  # output the image

  sum_image_r *= params.scale / len(args)
  sum_image_g *= params.scale / len(args)
  sum_image_b *= params.scale / len(args)

  if params.greyscale:
    save_image_gs(params.output, sum_image_r+sum_image_g+sum_image_b)
  else:
    save_image(params.output, sum_image_r, sum_image_g, sum_image_b)

if __name__ == '__main__':
  import sys
  run(sys.argv[1:])
