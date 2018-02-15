from __future__ import absolute_import, division, print_function

def Rt(xyr, xym):
  '''Implement https://en.wikipedia.org/wiki/Procrustes_analysis to match
  moving to referene.'''

  from dials.array_family import flex
  import math

  xr, yr = xyr.parts()
  xm, ym = xym.parts()

  # compute centre of mass shift
  xr0 = flex.sum(xr) / xr.size()
  yr0 = flex.sum(yr) / yr.size()

  xm0 = flex.sum(xm) / xm.size()
  ym0 = flex.sum(ym) / ym.size()

  dx = xm0 - xr0
  dy = ym0 - yr0

  print("COM shift: %f %f" % (dx, dy))

  xr -= xr0
  yr -= yr0

  xm -= xm0
  ym -= ym0

  # compute angle theta
  tan_theta = sum([_xm * _yr - _ym * _xr for _xr, _yr, _xm, _ym in
                   zip(xr, yr, xm, ym)]) / \
              sum([_xm * _xr + _ym * _yr for _xr, _yr, _xm, _ym in
                   zip(xr, yr, xm, ym)])
  theta = math.atan(tan_theta)

  print("Rotation: %f degrees" % (theta * 180.0 / math.pi))

  # compose Rt matrix, verify that the RMSD is small between xyr and Rt * xym


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

  print("%d of %d matches" % (matches.count(True), matches.size()))

  xyr = flex.vec2_double()
  xym = flex.vec2_double()

  for j in range(matches.size()):
    if not matches[j]:
      continue
    xym.append(mxy[j])
    xyr.append(rxy[ann.nn[j]])

  # compute Rt

  return Rt(xyr, xym)
