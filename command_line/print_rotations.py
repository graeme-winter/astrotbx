from __future__ import absolute_import, division, print_function

import iotbx.phil

phil_scope = iotbx.phil.parse("""
  alignments = rotations.json
    .type = path
""", process_includes=False)

def run(args):
  from dials.util.options import OptionParser
  import libtbx.load_env
  import json

  usage = "%s [options] " % (
    libtbx.env.dispatcher_name)

  parser = OptionParser(
    usage=usage,
    phil=phil_scope)

  params, options, args = parser.parse_args(show_diff_phil=True,
                                            return_unhandled=True)

  Rtds = json.load(open(params.alignments))
  for alignment in Rtds:
    R, t = alignment['R'], alignment['t']
    print('%8.5f %8.5f %8.5f %8.5f' % tuple(R), '%6.2f %6.2f' % tuple(t))

if __name__ == '__main__':
  import sys
  run(sys.argv[1:])
