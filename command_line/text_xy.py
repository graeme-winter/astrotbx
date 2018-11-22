from __future__ import absolute_import, division, print_function

import iotbx.phil

phil_scope = iotbx.phil.parse("""
  close = 10.0
    .type = float
  alignments = rotations.json
    .type = path
  prefix = stars
    .type = str
""", process_includes=False)


def run(args):
    from dials.util.options import OptionParser
    import libtbx.load_env

    usage = "%s [options] stars.pickle alignments=rotations.json" % (
        libtbx.env.dispatcher_name)

    parser = OptionParser(
        usage=usage,
        phil=phil_scope)

    params, options, args = parser.parse_args(show_diff_phil=True,
                                              return_unhandled=True)

    from dials.array_family import flex
    import cPickle as pickle
    import json

    if params.alignments:
        Rtds = json.load(open(params.alignments))
    else:
        Rtds = []
    stars = None

    for arg in args:
        tmp_stars = pickle.load(open(arg))
        if not stars:
            stars = tmp_stars
        else:
            stars.extend(tmp_stars)

    x, y, z = stars['xyzobs.px.value'].parts()

    zs = sorted(set(z))

    if not Rtds:
        for _ in zs:
            Rtds.append({'R': (1, 0, 0, 1), 't': (
                0, 0), 'd': 0, 'n': 0, 'dt': 0})

    assert len(Rtds) == len(zs)

    results = {}

    from scitbx import matrix

    for _z, alignment in zip(zs, Rtds):
        _x = x.select(z == _z)
        _y = y.select(z == _z)
        R, t = alignment['R'], alignment['t']
        _R = matrix.sqr(R)
        _xy = [_R * matrix.col((__x, __y)) + matrix.col(t)
               for __x, __y in zip(_x, _y)]
        with open('%s_%02d.dat' % (params.prefix, int(_z)), 'w') as f:
            for __xy in _xy:
                f.write('%f %f\n' % __xy.elems)


if __name__ == '__main__':
    import sys
    run(sys.argv[1:])
