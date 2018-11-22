from __future__ import absolute_import, division, print_function


class empty:
    pass


def background(image, mean_bg):
    from scitbx.random import variate, poisson_distribution
    dy, dx = image.focus()
    g = variate(poisson_distribution(mean=mean_bg))
    for j in range(dy):
        for i in range(dx):
            image[j, i] += next(g)
    return image


def random_positions(n, amount):
    from scitbx.random import variate, normal_distribution
    from dials.array_family import flex
    g = variate(normal_distribution(mean=0, sigma=amount))
    xy = flex.vec2_double(n)
    for j in range(n):
        xy[j] = (next(g), next(g))
    return xy


def make_test_image():
    from scitbx import matrix
    from dials.array_family import flex
    import random
    import math

    xmin, xmax = 0, 4272
    ymin, ymax = 0, 2848
    buffer = 100
    n = 30

    # generate n random positions - well within field of view

    x = flex.double(n)
    y = flex.double(n)
    z = flex.double(n, 0.0)

    for j in range(n):
        x[j] = random.uniform(xmin + buffer, xmax - buffer)
        y[j] = random.uniform(ymin + buffer, ymax - buffer)

    r = background(flex.double(flex.grid(ymax, xmax), 0.0), 3)
    g = background(flex.double(flex.grid(ymax, xmax), 0.0), 3)
    b = background(flex.double(flex.grid(ymax, xmax), 0.0), 3)

    # add some stars

    for xy in zip(x, y):
        star_x, star_y = random_positions(1000, 1).parts()
        star_x += xy[0]
        star_y += xy[1]
        for i, j in zip(star_x.iround(), star_y.iround()):
            r[j, i] += 1
            g[j, i] += 1
            b[j, i] += 1

    from astrotbx.input_output.saver import save_image
    save_image('example.png', r, g, b)


def test_finder():
    pass


def test_matcher():
    from scitbx import matrix
    from dials.array_family import flex
    import random
    import math

    xmin, xmax = 0, 4272
    ymin, ymax = 0, 2848
    buffer = 100
    n = 30

    # generate n random positions - well within field of view

    x = flex.double(n)
    y = flex.double(n)
    z = flex.double(n, 0.0)

    for j in range(n):
        x[j] = random.uniform(xmin + buffer, xmax - buffer)
        y[j] = random.uniform(ymin + buffer, ymax - buffer)

    # generate small rotation / translation - 0.25 degrees is one minute
    # of earth rotation

    s = 0.25 * math.pi / 360

    theta = random.uniform(-s, s)

    dx = random.uniform(-3, 3)
    dy = random.uniform(-3, 3)

    R = matrix.sqr([math.cos(theta), -math.sin(theta),
                    math.sin(theta), math.cos(theta)])

    t = matrix.col((dx, dy))

    # now apply

    x2 = flex.double(n)
    y2 = flex.double(n)

    for j in range(n):
        xy = (R * (x[j], y[j]) + t).elems
        x2[j], y2[j] = xy

    params = empty()
    params.close = 10

    # now feed the monster
    from astrotbx.algorithms.match import matcher

    # cast to reflection tables
    reference = flex.reflection_table()
    reference['xyzobs.px.value'] = flex.vec3_double(x, y, z)

    moving = flex.reflection_table()
    moving['xyzobs.px.value'] = flex.vec3_double(x2, y2, z)

    R2, t2, d, n = matcher(reference, moving, params)

    # assert results
    assert d < 1e-6
    assert sum((R2 * R - matrix.sqr((1, 0, 0, 1))).elems) < 1e-9
    assert sum((- R2.inverse() * t2 - t).elems) < 1e-9


if __name__ == '__main__':
    test_matcher()
    make_test_image()
