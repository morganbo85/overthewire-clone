#!/usr/bin/env python3
import sys, random, string

# usage: make_notes.py outpath flagfile lines
out = sys.argv[1]
flagfile = sys.argv[2]
lines = int(sys.argv[3])

with open(flagfile) as f:
    flag = f.read().strip()

# generate many noisy lines; place flag at a random position
pos = random.randrange(lines)
with open(out, "w") as f:
    for i in range(lines):
        if i == pos:
            f.write("Note {}: {}\n".format(i, flag))
        else:
            # random alphanum line
            l = ''.join(random.choices(string.ascii_letters + string.digits + "    ", k=60))
            f.write(f"Note {i}: {l}\n")