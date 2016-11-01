#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys

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

    forig = open(orig_file)
    prev_pos = 0
    new_num = 0
    for line in sys.stdin:
        pos = int(line.strip())
        diff = pos - prev_pos
        assert diff >= 0
        with open(new_model % (new_num), 'w') as fdest:
            copy(forig, fdest, diff)
        prev_pos = pos
        new_num += 1

    # Copy last chunk
    with open(new_model % (new_num), 'w') as fdest:
        copy(forig, fdest, 0)

if __name__ == '__main__':
    main()
