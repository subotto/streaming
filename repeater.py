#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import struct

def main():
    filename = sys.argv[1]

    with open(filename) as fin:
        content = fin.read()

    # Add length tag
    content = struct.pack("!I", len(content)) + content

    num = 0
    try:
        while True:
            sys.stdout.write(content)
            print >> sys.stderr, num
            num += 1
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
