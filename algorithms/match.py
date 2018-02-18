from __future__ import absolute_import, division, print_function

def Rt(xyr, xym):
  '''Implement https://en.wikipedia.org/wiki/Procrustes_analysis to match
  moving to reference.'''

  from dials.array_family import flex
  import math

  n = xyr.size()
  assert xym.size() == n

  xr, yr = xyr.parts()
  xm, ym = xym.parts()

  # compute centre of mass shift
  xr0, yr0 = flex.sum(xr) / xr.size(), flex.sum(yr) / yr.size()
  xm0, ym0 = flex.sum(xm) / xm.size(), flex.sum(ym) / ym.size()
  dx, dy = xr0 - xm0, yr0 - ym0

  xr, yr = xr - xr0, yr - yr0
  xm, ym = xm - xm0, ym - ym0

  # compute angle theta
  tan_theta = sum([_xm * _yr - _ym * _xr for _xr, _yr, _xm, _ym in
                   zip(xr, yr, xm, ym)]) / \
              sum([_xm * _xr + _ym * _yr for _xr, _yr, _xm, _ym in
                   zip(xr, yr, xm, ym)])
  theta = math.atan(tan_theta)

  # compose Rt matrix, verify that the RMSD is small between xyr and Rt * xym
  from scitbx import matrix
  R = matrix.sqr((math.cos(theta), - math.sin(theta),
                  math.sin(theta), math.cos(theta)))

  rmsd = 0
  for j, (_xm, _ym) in enumerate(zip(xm, ym)):
    _xr, _yr = xr[j], yr[j]
    _xmr, _ymr = R * (_xm, _ym)
    rmsd += (_xmr - _xr) ** 2 + (_ymr - _yr) ** 2

  rmsd /= n

  # now compute additional t component due to rotation about origin not centre
  # of mass

  t0 = matrix.col((xm0, ym0)) - R * (xm0, ym0)
  t = t0 + matrix.col((dx, dy))

  return R, t.elems, math.sqrt(rmsd), n

def IQR(array):
  n = array.size()
  median = array[int(round(0.5 * n))]
  q1 = array[int(round(0.25 * n))]
  q3 = array[int(round(0.75 * n))]
  return q1, median, q3, q3 - q1

def matcher(reference, moving, params):
  from annlib_ext import AnnAdaptor as ann_adaptor
  from dials.array_family import flex

  rxyz = reference['xyzobs.px.value'].parts()
  mxyz = moving['xyzobs.px.value'].parts()

  rxy = flex.vec2_double(rxyz[0], rxyz[1])
  mxy = flex.vec2_double(mxyz[0], mxyz[1])

  ann = ann_adaptor(rxy.as_double().as_1d(), 2)
  ann.query(mxy.as_double().as_1d())
  distances = flex.sqrt(ann.distances)

  matches = (distances < params.close)

  xyr = flex.vec2_double()
  xym = flex.vec2_double()

  for j in range(matches.size()):
    if not matches[j]:
      continue
    xym.append(mxy[j])
    xyr.append(rxy[ann.nn[j]])

  # filter outliers - use IQR etc.
  dxy = xym - xyr

  dx, dy = dxy.parts()

  iqx = IQR(dx.select(flex.sort_permutation(dx)))
  iqy = IQR(dy.select(flex.sort_permutation(dy)))

  keep_x = (dx > (iqx[0] - iqx[3])) & (dx < (iqx[2] + iqx[3]))
  keep_y = (dy > (iqy[0] - iqy[3])) & (dy < (iqy[2] + iqy[3]))
  keep = keep_x & keep_y
  xyr = xyr.select(keep)
  xym = xym.select(keep)

  # compute Rt

  R, t, d, n = Rt(xyr, xym)

  # verify matches in original image coordinate system

  from scitbx import matrix
  import math
  _R = matrix.sqr(R)
  rmsd = 0.0
  for j, _xym in enumerate(xym):
    _xymm = _R * _xym + matrix.col(t)
    rmsd += (matrix.col(xyr[j]) - _xymm).length() ** 2
  assert abs(math.sqrt(rmsd / xym.size()) - d) < 1e-6

  return R, t, d, n
