from __future__ import absolute_import, division, print_function

def rotate_translate_array(image, R, t):
  from dials.array_family import flex
  from scipy.ndimage import affine_transform
  import numpy

  matrix = numpy.array([[R[0], R[1]], [R[2], R[3]]])

  return flex.double(affine_transform(image.as_numpy_array(), matrix, offset=t))
