'''
Copyright (c) 2015 Geoffrey Sneddon

Permission is hereby granted,  free of charge,  to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to  use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
'''

from __future__ import division
from AppKit import NSColor


__all__ = ["rgb", "passes_AA", "passes_AAA"]


def getPercievedColor(rgba1, rgba2):
    # thank's Tal
    color1 = NSColor.colorWithCalibratedRed_green_blue_alpha_(*rgba1)
    color2 = NSColor.colorWithCalibratedRed_green_blue_alpha_(*rgba2[:-1], 1)
    color3 = color1.blendedColorWithFraction_ofColor_(rgba2[-1], color2)
    r = color3.redComponent()
    g = color3.greenComponent()
    b = color3.blueComponent()
    a = color3.alphaComponent()
    return r,g,b,a 

def invertColor(rgba):
    r,g,b,a = list(rgba)
    return (1-r,1-g,1-b,a)

def rgb(rgb1, rgb2):
    if len(rgb1) == 4:
        rgb1 = tuple(list(rgb1)[:-1])
    if len(rgb2) == 4:
        rgb2 = tuple(list(rgb2)[:-1])
        
    for r, g, b in (rgb1, rgb2):
        if not 0.0 <= r <= 1.0:
            raise ValueError("r is out of valid range (0.0 - 1.0)")
        if not 0.0 <= g <= 1.0:
            raise ValueError("g is out of valid range (0.0 - 1.0)")
        if not 0.0 <= b <= 1.0:
            raise ValueError("b is out of valid range (0.0 - 1.0)")

    l1 = _relative_luminance(*rgb1)
    l2 = _relative_luminance(*rgb2)

    if l1 > l2:
        return (l1 + 0.05) / (l2 + 0.05)
    else:
        return (l2 + 0.05) / (l1 + 0.05)


def _relative_luminance(r, g, b):
    r = _linearize(r)
    g = _linearize(g)
    b = _linearize(b)

    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _linearize(v):
    if v <= 0.03928:
        return v / 12.92
    else:
        return ((v + 0.055) / 1.055) ** 2.4


def passes_AA(contrast, large=False):
    if large:
        return contrast >= 3.0
    else:
        return contrast >= 4.5


def passes_AAA(contrast, large=False):
    if large:
        return contrast >= 4.5
    else:
        return contrast >= 7.0
