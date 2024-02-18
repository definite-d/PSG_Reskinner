#  PSG_Reskinner
#
#  Enables changing the themes of your PySimpleGUI windows and elements
#  instantaneously on the fly without the need for re-instantiating the window.
#
#  MIT License
#
#  Copyright (c) 2023 Divine Afam-Ifediogor
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

from math import cos, sin, pi, sqrt, pow

# Easing functions adapted from https://easings.net

EASE_CONSTANT = lambda x: x
EASE_IN_SINE = lambda x: 1 - cos((x * pi) / 2)
EASE_OUT_SINE = lambda x: sin((x * pi) / 2)
EASE_IN_OUT_SINE = lambda x: -(cos(x * pi) - 1) / 2
EASE_IN_QUAD = lambda x: pow(x, 2)
EASE_OUT_QUAD = lambda x: 1 - (1 - x) * (1 - x)
EASE_IN_OUT_QUAD = lambda x: 2 * pow(x, 2) if x < 0.5 else 1 - pow(-2 * x + 2, 2) / 2
EASE_IN_CUBIC = lambda x: pow(x, 3)
EASE_OUT_CUBIC = lambda x: 1 - pow(1 - x, 3)
EASE_IN_OUT_CUBIC = lambda x: 4 * pow(x, 3) if x < 0.5 else 1 - pow(-2 * x + 2, 3) / 2
EASE_IN_QUART = lambda x: pow(x, 4)
EASE_OUT_QUART = lambda x: 1 - pow(1 - x, 4)
EASE_IN_OUT_QUART = lambda x: 8 * pow(x, 4) if x < 0.5 else 1 - pow(-2 * x + 2, 4) / 2
EASE_IN_QUINT = lambda x: pow(x, 5)
EASE_OUT_QUINT = lambda x: 1 - pow(1 - x, 5)
EASE_IN_OUT_QUINT = lambda x: 16 * pow(x, 5) if x < 0.5 else 1 - pow(-2 * x + 2, 5) / 2
EASE_IN_EXPO = lambda x: 0 if x == 0 else pow(2, 10 * x - 10)
EASE_OUT_EXPO = lambda x: 1 if x == 1 else 1 - pow(2, -10 * x)
EASE_IN_OUT_EXPO = (
    lambda x: 0
    if x == 0
    else 1
    if x == 1
    else pow(2, 20 * x - 10) / 2
    if x < 0.5
    else (2 - pow(2, -20 * x + 10)) / 2
)
EASE_IN_CIRC = lambda x: 1 - sqrt(1 - pow(x, 2))
EASE_OUT_CIRC = lambda x: sqrt(1 - pow(x - 1, 2))
EASE_IN_OUT_CIRC = (
    lambda x: (1 - sqrt(1 - pow(2 * x, 2))) / 2
    if x < 0.5
    else (sqrt(1 - pow(-2 * x + 2, 2)) + 1) / 2
)


def _ease_out_bounce(x):
    n1 = 7.5625
    d1 = 2.75
    if x < 1 / d1:
        return n1 * x * x
    elif x < 2 / d1:
        x -= 1.5
        return n1 * (x / d1) * x + 0.75
    elif x < 2.5 / d1:
        x -= 2.25
        return n1 * (x / d1) * x + 0.9375
    else:
        x -= 2.625
        return n1 * (x / d1) * x + 0.984375


EASE_OUT_BOUNCE = lambda x: _ease_out_bounce(x)  # For uniformity.
EASE_IN_BOUNCE = lambda x: 1 - _ease_out_bounce(1 - x)
EASE_IN_OUT_BOUNCE = (
    lambda x: (1 - _ease_out_bounce(1 - 2 * x)) / 2
    if x < 0.5
    else (1 + _ease_out_bounce(2 * x - 1)) / 2
)
