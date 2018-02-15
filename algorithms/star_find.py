from __future__ import absolute_import, division, print_function

def find(greyscale_flex, params):
  '''Find stars on input greyscale flex image.'''

  from dials.algorithms.spot_finding.threshold import \
    DispersionThresholdStrategy
  from dials.model.data import PixelList
  from dials.model.data import PixelListLabeller
  from dials.array_family import flex

  thresholder = DispersionThresholdStrategy(gain=params.gain)
  mask = flex.bool(greyscale_flex.size(), True)
  mask.reshape(flex.grid(*greyscale_flex.focus()))

  threshold_mask = thresholder(greyscale_flex, mask=mask)
  plist = PixelList(0, greyscale_flex, threshold_mask)

  pixel_labeller = PixelListLabeller()
  pixel_labeller.add(plist)

  creator = flex.PixelListShoeboxCreator(
    pixel_labeller, 0, 0, True, params.min_size, params.max_size, False)
  shoeboxes = creator.result()

  # remove nonsense
  size = creator.spot_size()
  big = size > params.max_size
  small = size < params.min_size
  bad = big | small
  shoeboxes = shoeboxes.select(~bad)

  centroid = shoeboxes.centroid_valid()
  intensity = shoeboxes.summed_intensity()
  observed = flex.observation(shoeboxes.panels(), centroid, intensity)

  stars = flex.reflection_table(observed, shoeboxes)
  return stars
