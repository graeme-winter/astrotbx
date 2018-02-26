from dials.algorithms.image import filter
from astrotbx.input_output.loader import load_image_gs
from dials.array_family import flex

import sys
image = load_image_gs(sys.argv[1])
disp = filter.index_of_dispersion_filter(image, (3, 3)).index_of_dispersion()
hist = flex.histogram(disp.as_1d(), data_min=0, data_max=100, n_slots=1000)
for c, v in zip(hist.slot_centers(), hist.slots()):
  print c, v
