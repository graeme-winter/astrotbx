from __future__ import absolute_import, division, print_function

def Rt(xyr, xym):
  pass

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
