from __future__ import division, print_function

import iotbx.phil

phil_scope = iotbx.phil.parse("""
  log_n = false
    .type = bool
""", process_includes=False)


def correlation(a, b):
    from astrotbx.input_output.loader import load_image_gs
    from dials.array_family import flex
    data_a = load_image_gs(a).as_1d()
    data_b = load_image_gs(b).as_1d()
    c = flex.linear_correlation(data_a, data_b)
    print(c.coefficient())


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

    correlation(args[0], args[1])


if __name__ == '__main__':
    import sys
    import matplotlib
    matplotlib.use('Agg')
    run(sys.argv[1:])
