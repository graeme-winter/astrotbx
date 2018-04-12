from __future__ import absolute_import, division, print_function

import iotbx.phil

phil_scope = iotbx.phil.parse("""
  output = hot.pickle
    .type = path
  gain = 10.0
    .type = float
  include scope astrotbx.input_output.loader.phil_scope
""", process_includes=True)

def run(args):
  from dials.util.options import OptionParser
  import libtbx.load_env

  usage = "%s [options] *ARW" % (
    libtbx.env.dispatcher_name)

  parser = OptionParser(
    usage=usage,
    phil=phil_scope)

  params, options, args = parser.parse_args(show_diff_phil=True,
                                            return_unhandled=True)

  from astrotbx.input_output.loader import load_image_gs, load_raw_image_gs
  from astrotbx.algorithms.star_find import hot
  from dials.array_family import flex

  raws = ['arw']

  total = None

  n = 0
  for arg in args:
    n += 1
    exten = arg.split('.')[-1].lower()
    if exten in raws:
      image = load_raw_image_gs(arg, params.raw)
    else:
      image = load_image_gs(arg)
    signal = hot(image, params).as_1d()
    if total is None:
      total = signal.as_int()
    else:
      total += signal.as_int()
  h_total = flex.histogram(total.as_double(),
                           data_min=-0.5, data_max=n+0.5, n_slots=n+1)
  for c, v in zip(h_total.slot_centers(), h_total.slots()):
    print(c, v)
  total.reshape(flex.grid(*image.focus()))

  if params.output:
    import cPickle as pickle
    with open(params.output, 'w') as fout:
      pickle.dump(total, fout, protocol=pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
  import sys
  run(sys.argv[1:])
