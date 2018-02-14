import sys
import numpy
import math
from scipy.ndimage import affine_transform
from PIL import Image

theta = 1.2 * math.pi / 180.0
shift_x = 1.1
shift_y = - 3.2

mtrx = numpy.array([[math.cos(theta), - math.sin(theta)],
                    [math.sin(theta), math.cos(theta)]])
offset = shift_x, shift_y

r, g, b = Image.open(sys.argv[1]).split()

ri = numpy.asarray(r)
rm = Image.fromarray(affine_transform(ri, mtrx, offset=offset))
gi = numpy.asarray(g)
gm = Image.fromarray(affine_transform(gi, mtrx, offset=offset))
bi = numpy.asarray(b)
bm = Image.fromarray(affine_transform(bi, mtrx, offset=offset))

Image.merge('RGB', (rm, gm, bm)).save('turned.png')

