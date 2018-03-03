from __future__ import division, print_function

import iotbx.phil

phil_scope = iotbx.phil.parse("""
  output = histogram.dat
    .type = path
  include scope astrotbx.input_output.loader.phil_scope
""", process_includes=True)

def histogram(params, images):
  from astrotbx.input_output.loader import load_raw_image
  from dials.array_family import flex

  hr = None
  hg = None
  hb = None

  for image in images:
    r, g, b = load_raw_image(image, params=params.raw)

    tr = flex.histogram(r.as_1d(), data_min=0, data_max=65535, n_slots=4096)
    tg = flex.histogram(g.as_1d(), data_min=0, data_max=65535, n_slots=4096)
    tb = flex.histogram(b.as_1d(), data_min=0, data_max=65535, n_slots=4096)

    if hr is None:
      hr = tr
    else:
      hr.update(tr)

    if hg is None:
      hg = tg
    else:
      hg.update(tg)

    if hb is None:
      hb = tb
    else:
      hb.update(tb)

  with open(params.output, 'w') as f:
    for cn in zip(hr.slot_centers(), hr.slots(), hg.slots(), hb.slots()):
      f.write('%.2f %d %d %d\n' % cn)

def run(args):
  from dials.util.options import OptionParser
  import libtbx.load_env
  import json

  usage = "%s [options] DSC03206.ARW" % (
    libtbx.env.dispatcher_name)

  parser = OptionParser(
    usage=usage,
    phil=phil_scope)

  params, options, args = parser.parse_args(show_diff_phil=True,
                                            return_unhandled=True)

  histogram(params, args)

if __name__ == '__main__':
  import sys
  import matplotlib
  run(sys.argv[1:])
