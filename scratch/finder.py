import sys
import numpy
import math
from scipy.ndimage import affine_transform
from PIL import Image

from dials.array_family import flex

# read image into memory, sum RGB channels, convert to flex type
r, g, b = map(numpy.asarray, Image.open(sys.argv[1]).split())
gs = numpy.double(r) + numpy.double(g) + numpy.double(b)
gsd = flex.double(gs)

# star finding
from dials.algorithms.spot_finding.threshold import DispersionThresholdStrategy
from dials.model.data import PixelList
from dials.model.data import PixelListLabeller

# set gain 10 to only catch strong stars
thresholder = DispersionThresholdStrategy(gain=10)
mask = flex.bool(gsd.size(), True)
mask.reshape(flex.grid(*gsd.focus()))

threshold_mask = thresholder(gsd, mask=mask)
plist = PixelList(0, gsd, threshold_mask)

pixel_labeller = PixelListLabeller()
pixel_labeller.add(plist)

# smallest star is 3 pixels, largest is 100
creator = flex.PixelListShoeboxCreator(
    pixel_labeller, 0, 0, True, 3, 100, False)
shoeboxes = creator.result()

# remove nonsense
size = creator.spot_size()
big = size > 100
small = size < 3
bad = big | small
shoeboxes = shoeboxes.select(~bad)

centroid = shoeboxes.centroid_valid()
intensity = shoeboxes.summed_intensity()
observed = flex.observation(shoeboxes.panels(), centroid, intensity)

reflections = flex.reflection_table(observed, shoeboxes)
i = reflections['intensity.sum.value']
x, y, z = reflections['xyzobs.px.value'].parts()

for _x, _y, _i in zip(x, y, i):
  print _x, _y, _i
