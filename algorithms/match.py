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

  return R, (dx, dy), math.sqrt(rmsd), n

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

  # compute Rt

  return Rt(xyr, xym)
