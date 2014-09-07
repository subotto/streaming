#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import struct

def main():
    num = 0
    try:
        while True:
            length_tag = sys.stdin.read(4)
            length, = struct.unpack("!I", length_tag)
            imdata = sys.stdin.read(length)
            if imdata == '':
                break
            sys.stdout.write(imdata)
            num += 1
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
