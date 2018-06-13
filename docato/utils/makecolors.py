#!/usr/bin/env python

import argparse, random

aparser = argparse.ArgumentParser()
aparser.add_argument('-t', type = str, default = None, help = 'path to a file containing template to generate lines')
aparser.add_argument('-a', type = float, default = 0.3, help = 'Transparency (aplha channel)')
aparser.add_argument('-n', type = int, default = 200, help = 'how many lines to generate')
aparser.add_argument('-b', type = float, default = 1.0, help = 'brightness, 0 is the darkest and 1 is the brightest')

args = aparser.parse_args()

if args.t:
    with open(args.t, 'r') as f:
        tmpl = f.read()
else:
    tmpl = '.color-{0} {{ background-color: {1} }}\n'

def gen_color(brightness = 1.0, transparency = 1.0):
    r = random.random()
    g = random.random()
    b = random.random()
    norm = max(r, g, b) * brightness
    max_value = 255.0 * brightness
    return 'rgba(%d, %d, %d, %f)' % (r * max_value / norm,
                                     g * max_value / norm,
                                     b * max_value / norm,
                                     transparency)

print ''.join(tmpl.format(i, gen_color(args.b, args.a)) for i in xrange(args.n))
