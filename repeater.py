#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

def main():
    filename = sys.argv[1]

    with open(filename) as fin:
        content = fin.read()

    try:
        while True:
            sys.stdout.write(content)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
