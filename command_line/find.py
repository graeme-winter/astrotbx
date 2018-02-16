from __future__ import absolute_import, division, print_function

import iotbx.phil

phil_scope = iotbx.phil.parse("""
  gain = 10.0
    .type = float
  min_size = 3
    .type = int
  max_size = 300
    .type = int
  output = stars.pickle
    .type = path
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

  from astrotbx.input_output.loader import load_image_gs
  from astrotbx.algorithms.star_find import find
  from dials.array_family import flex

  all = None

  for j, arg in enumerate(args):
    image = load_image_gs(arg)
    stars = find(image, params)
    print("On %s found %d stars" % (arg, stars.size()))
    if all is None:
      all = stars
    else:
      x, y, z = stars['xyzobs.px.value'].parts()
      z += j
      stars['xyzobs.px.value'] = flex.vec3_double(x, y, z)
      all.extend(stars)

  print("Saving %d stars to %s" % (all.size(), params.output))
  all.as_pickle(params.output)

if __name__ == '__main__':
  import sys
  run(sys.argv[1:])
