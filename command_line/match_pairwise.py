from __future__ import absolute_import, division, print_function

import iotbx.phil

phil_scope = iotbx.phil.parse("""
  far = 10.0
    .type = float
  close = 0.0
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

    usage = "%s [options] stars.pickle" % (
        libtbx.env.dispatcher_name)

    parser = OptionParser(
        usage=usage,
        phil=phil_scope)

    params, options, args = parser.parse_args(show_diff_phil=True,
                                              return_unhandled=True)

    from dials.array_family import flex
    import cPickle as pickle
    from astrotbx.algorithms.match import matcher, pair_up, compute_Rt

    stars = None

    for arg in args:
        tmp_stars = pickle.load(open(arg))
        if not stars:
            stars = tmp_stars
        else:
            stars.extend(tmp_stars)

    z = flex.floor(stars['xyzobs.px.value'].parts()[2]).iround()

    zs = sorted(set(z))

    Rtds = []
    Rtds.append({'R': (1, 0, 0, 1), 't': (0, 0), 'd': 0, 'n': 0, 'dt': 0})

    from scitbx import matrix
    import math

    datum0 = stars.select(z == zs[0])

    for j in range(len(zs) - 1):
        _r = zs[j]
        _z = zs[j + 1]

        datum = stars.select(z == _r)
        move = stars.select(z == _z)

        dt = move['timestamp'][0]

        # get the moves for this step
        R, t, d, n = matcher(datum, move, params)

        # compose with previous to map back to datum i.e. 0-th image positions
        _R, _t = matrix.sqr(Rtds[-1]['R']), matrix.col(Rtds[-1]['t'])
        Rc = matrix.sqr(R) * _R
        tc = matrix.sqr(R) * _t + matrix.col(t)

        # refine w.r.t. datum positions... seems to drift
        rsel, msel = pair_up(datum0, move, params, Rc, tc)

        R1, t1, d1, n1 = compute_Rt(datum0.select(rsel), move.select(msel))

        # now use this stack to match up with the datum stars i.e. apply to star
        # positions, match then use that iselection to derive the full Rt =>
        # will involve refactor... N.B. need to do outlier rejection after matching
        # but before mapping back / Rt calculation.

        # the re-compute the full Rt from datum to this time point

        Rtds.append({'R': R1.elems, 't': t1, 'd': d1, 'n': n1, 'dt': dt})

    for j, Rtd in enumerate(Rtds):
        print('%3d %.4f %3d %4d' % (j, Rtd['d'], Rtd['n'], Rtd['dt']))

    import json
    json.dump(Rtds, open(params.output, 'w'))


if __name__ == '__main__':
    import sys
    run(sys.argv[1:])
