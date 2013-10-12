#!/usr/bin/python

import gc
import os
import re
import signal
import struct
import sys
from operator import itemgetter

chars = r"A-Za-z0-9/\-:.,_$%'\"()[\]<> "
min_length = 10
scores = []
top_score = 0

regexp = "[%s]{%d,}" % (chars, min_length)
pattern = re.compile(regexp)
regexpc = "[%s]{1,}" % chars
patternc = re.compile(regexpc)

def high_scores(signal, frame):
    print "\nTop 20 base address candidates:"
    for score in sorted(scores, key=itemgetter(1), reverse=True)[:20]:
        print "0x%x\t%d" % score
    sys.exit(0)

def get_pointers(f):
    table = {}
    f.seek(0)
    while True:
        try:
            value = struct.unpack("<L", f.read(4))[0]
            try:
                table[value] += 1
            except KeyError:
                table[value] = 1
        except:
            break
    return table

def get_strings(f, size):
    table = set([])
    tbladd = table.add
    offset = 0
    while True:
        if offset >= size:
            break
        f.seek(offset)
        try:
            data = f.read(10)
        except:
            break
        match = pattern.match(data)
        if match:
            f.seek(offset - 1)
            try:
                char = f.read(1)
            except:
                continue
            if not patternc.match(char):
                tbladd(offset)
                offset += len(match.group(0))
        offset += 1
    return table

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "%s: <image>" % sys.argv[0]
        exit()

    infile = sys.argv[1]
    size = os.path.getsize(infile)
    f = open(infile, "rb")
    scores = []

    print "Scanning binary for strings..."
    str_table = get_strings(f, size)
    print "Total strings found: %d" % len(str_table)

    print "Scanning binary for pointers..."
    ptr_table = get_pointers(f)
    print "Total pointers found: %d" % len(ptr_table)

    f.close()
    gc.disable()
    signal.signal(signal.SIGINT, high_scores)

    for base in xrange(0, 0xf0000000, 0x1000):
        if base % 0x10000 == 0:
            print "Trying base address 0x%x" % base
        score = 0
        for ptr in ptr_table.keys():
            if ptr < base:
                #print "Removing pointer 0x%x from table" % ptr
                del ptr_table[ptr]
                continue
            if ptr >= (base + size):
                continue
            offset = ptr - base
            if offset in str_table:
                score += ptr_table[ptr]
        scores.append((base, score))
        if score >= top_score:
            top_score = score
            print "New highest score, 0x%x: %d" % (base, score)

    high_scores(0, 0)
