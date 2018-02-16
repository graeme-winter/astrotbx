from __future__ import absolute_import, division, print_function

import iotbx.phil

phil_scope = iotbx.phil.parse("""
  close = 10.0
    .type = float
  output = rotations.json
    .type = path
  randomize = 0.0
    .type = float
""", process_includes=False)

def randomize(values, amount):
  from scitbx.random import variate, normal_distribution
  from dials.array_family import flex
  g = variate(normal_distribution(mean=0, sigma=amount))
  shift = flex.double(values.size())
  for j in range(values.size()):
    shift[j] = next(g)
  return values + shift

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

  from dials.array_family import flex
  import cPickle as pickle
  from astrotbx.algorithms.match import matcher

  stars = None

  for arg in args:
    tmp_stars = pickle.load(open(arg))
    if not stars:
      stars = tmp_stars
    else:
      stars.extend(tmp_stars)

  z = stars['xyzobs.px.value'].parts()[2]

  zs = list(set(z))
  zs.sort()

  datum_z = zs[len(zs) // 2]
  datum = stars.select(z == datum_z)

  Rtds = []

  for _z in zs:
    if _z == datum_z:
      Rtds.append({'R':(1,0,0,1), 't':(0,0), 'd':0, 'n':datum.size()})
      continue
    move = stars.select(z == _z)
    if params.randomize:
      x, y, a = move['xyzobs.px.value'].parts()
      x = randomize(x, params.randomize)
      y = randomize(y, params.randomize)
      move['xyzobs.px.value'] = flex.vec3_double(x, y, a)

    R, t, d, n = matcher(datum, move, params)
    Rtds.append({'R':R.elems, 't':t, 'd':d, 'n':n})

  for j, Rtd in enumerate(Rtds):
    print('%3d %.4f %3d' % (j, Rtd['d'], Rtd['n']))

  import json
  json.dump(Rtds, open(params.output, 'w'))

if __name__ == '__main__':
  import sys
  run(sys.argv[1:])
