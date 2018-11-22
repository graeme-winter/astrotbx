from __future__ import absolute_import, division, print_function


def info(filename):
    '''Generate information from EXIF headers.'''

    import exifread
    import datetime
    import calendar

    ts = 'EXIF DateTimeOriginal'

    result = {}

    with open(filename) as f:
        tags = exifread.process_file(f, details=False, stop_tag=ts)
        dt = datetime.datetime.strptime(str(tags[ts]), '%Y:%m:%d %H:%M:%S')
        result['timestamp'] = calendar.timegm(dt.timetuple())

    return result
