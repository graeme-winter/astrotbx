from __future__ import absolute_import, division, print_function

import iotbx.phil

phil_scope = iotbx.phil.parse("""
  min = -32
    .type = float
  max = 32
    .type = float
  bins = 64
    .type = int
  histogram = None
    .type = path
  log = false
    .type = bool
  output = None
    .type = path
  png = None
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
  t_sqr = None

  # first build up mean dark image

  for arg in args:
    image = load_dark_image(arg, params.raw)
    if total is None:
      total = image
      t_sqr = image ** 2
    else:
      total += image
      t_sqr += image ** 2

  dark = total * (1.0 / len(args))
  dvar = flex.sqrt(t_sqr * (1.0 / len(args)) - dark)

  # then subtract it from each other image and look at residual

  hist = None

  for j, arg in enumerate(args):
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

  if params.histogram:
    v = hist.slot_centers().as_double()
    n = hist.slots().as_double()
    pyplot.bar(v, n, log=params.log)
    pyplot.savefig(params.histogram)

  # diagnostics
  print('Mean / min / max dark value: %.1f / %.1f / %.1f' %
        (flex.mean(dark), flex.min(dark), flex.max(dark)))
  print('Mean / min / max dark sigma: %.1f / %.1f / %.1f' %
        (flex.mean(dvar), flex.min(dvar), flex.max(dvar)))

  if params.output:
    import cPickle as pickle
    with open(params.output, 'w') as fout:
      pickle.dump(dark.iround().as_numpy_array(), fout,
                  protocol=pickle.HIGHEST_PROTOCOL)

  if params.png:
    from astrotbx.input_output.saver import save_image_gs
    save_image_gs(params.png, dark)

if __name__ == '__main__':
  import sys
  import matplotlib
  matplotlib.use('Agg')
  run(sys.argv[1:])
