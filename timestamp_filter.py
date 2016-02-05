#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import datetime
import tzlocal
import pytz
import os
import struct

from imgio import read_jpeg_frame, write_jpeg_frame

ENTRY_LEN = 20

def search_frame(fidx, timestamp, last=False):
    fidx.seek(0, os.SEEK_END)
    file_length = fidx.tell()
    assert file_length % ENTRY_LEN == 0
    length = file_length / ENTRY_LEN
    a = 0
    b = length

    while a + 1 != b:
        c = (a+b) / 2
        assert c != a
        assert c != b
        fidx.seek(c * ENTRY_LEN, os.SEEK_SET)
        entry = fidx.read(ENTRY_LEN)
        entry_num, entry_timestamp, entry_pos = struct.unpack("!IdQ", entry)
        if entry_timestamp <= timestamp:
            a = c
        else:
            b = c

    assert b == a + 1
    if last:
        a = b
    if a == length:
        return -1, None, -1
    fidx.seek(a * ENTRY_LEN, os.SEEK_SET)
    entry = fidx.read(ENTRY_LEN)
    return struct.unpack("!IdQ", entry)

def main():
    fin = open(sys.argv[1])
    fidx = open(sys.argv[1] + '-idx')
    fout = sys.stdout

    epoch = datetime.datetime(1970, 1, 1, tzinfo=pytz.UTC)
    begin = datetime.datetime.strptime(sys.argv[2], '%Y-%m-%d %H:%M:%S').replace(tzinfo=tzlocal.get_localzone())
    end = datetime.datetime.strptime(sys.argv[3], '%Y-%m-%d %H:%M:%S').replace(tzinfo=tzlocal.get_localzone())
    begin_ts = (begin - epoch).total_seconds()
    end_ts = (end - epoch).total_seconds()
    print >> sys.stderr, "Selecting timestamps from %f to %f" % (begin_ts, end_ts)

    begin_num, begin_ts, begin_pos = search_frame(fidx, begin_ts, last=False)
    end_num, end_ts, end_pos = search_frame(fidx, end_ts, last=True)
    print >> sys.stderr, "This means frames from %d to %d, or bytes from %d to %d" % (begin_num, end_num, begin_pos, end_pos)
    fidx.close()

    fin.seek(begin_pos, os.SEEK_SET)
    rem = end_pos - begin_pos
    while rem > 0:
        buf = fin.read(min(rem, 4096))
        rem -= len(buf)
        fout.write(buf)

if __name__ == '__main__':
    main()
