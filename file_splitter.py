#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import os
import fadvise

BUF_SIZE = 1024 * 1024

def copy(fin, fout, l):
    if l > 0:
        while l > 0:
            buf = fin.read(min(l, BUF_SIZE))
            l -= len(buf)
            fout.write(buf)
    else:
        while True:
            buf = fin.read(BUF_SIZE)
            if buf == '':
                return
            fout.write(buf)

def main():
    orig_file = sys.argv[1]
    new_model = sys.argv[2]
    if len(sys.argv) > 3:
        start_chunk = int(sys.argv[3])

    forig = open(orig_file)
    prev_pos = 0
    new_num = 0
    for line in sys.stdin:
        pos = int(line.strip())
        diff = pos - prev_pos
        assert diff >= 0
        if new_num >= start_chunk:
            filename = new_model % (new_num)
            with open(new_model % (new_num), 'w') as fdest:
                fadvise.posix_fadvise(forig.fileno(), 0, forig.tell(), fadvise.POSIX_FADV_DONTNEED)
                fadvise.posix_fadvise(forig.fileno(), forig.tell(), 0, fadvise.POSIX_FADV_SEQUENTIAL)
                fadvise.posix_fadvise(fdest.fileno(), 0, 0, fadvise.POSIX_FADV_SEQUENTIAL)
                copy(forig, fdest, diff)
        else:
            forig.seek(diff, os.SEEK_CUR)
        prev_pos = pos
        new_num += 1

    # Copy last chunk
    with open(new_model % (new_num), 'w') as fdest:
        copy(forig, fdest, 0)

if __name__ == '__main__':
    main()
