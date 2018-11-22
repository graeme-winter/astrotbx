from __future__ import absolute_import, division, print_function


def info(images):
    from scitbx.array_family import flex
    import rawpy
    import numpy

    import exifread
    import datetime
    import calendar

    ts = 'EXIF DateTimeOriginal'

    for image in images:
        with rawpy.imread(image) as raw:
            with open(image) as f:
                tags = exifread.process_file(f, details=False, stop_tag=ts)
                dt = datetime.datetime.strptime(
                    str(tags[ts]), '%Y:%m:%d %H:%M:%S')

            print("Time stamp:    ", calendar.timegm(dt.timetuple()))
            print("Pixel channels:", raw.color_desc)
            print("Black values:  ", raw.black_level_per_channel)
            print("Pattern:       ", raw.raw_pattern.tolist())
            print("White balance:  %.1f %.1f %.1f %.1f" %
                  tuple(raw.camera_whitebalance))
            sizes = raw.sizes._asdict()
            print("Size info:")
            for p in sizes:
                print("   %12s -> %s" % (p, str(sizes[p])))
            print("Array shape:   %d %d" % raw.raw_image.shape)
            print("Visible:       %d %d" % raw.raw_image_visible.shape)

            # close to overloaded i.e. within black level of 2^12
            thresh = 2**12 - raw.black_level_per_channel[0]
            print("Max raw:       %d" % (numpy.amax(raw.raw_image)))
            print(
                "N > %4d:      %d" %
                (thresh, (raw.raw_image > thresh).sum()))


if __name__ == '__main__':
    import sys
    info(sys.argv[1:])
