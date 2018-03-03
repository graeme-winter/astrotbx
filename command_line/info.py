from __future__ import absolute_import, division, print_function

def info(images):
  from scitbx.array_family import flex
  import rawpy
  import numpy

  for image in images:
    with rawpy.imread(image) as raw:
      print("Pixel channels:", raw.color_desc)
      print("Black values:  ", raw.black_level_per_channel)
      print("Pattern:       ", raw.raw_pattern.tolist())
      print("White balance:  %.1f %.1f %.1f %.1f" %
            tuple(raw.camera_whitebalance))
      sizes = raw.sizes._asdict()
      print("Size info:")
      for p in sizes:
        print("   %12s -> %s" % (p, str(sizes[p])))

if __name__ == '__main__':
  import sys
  info(sys.argv[1:])
