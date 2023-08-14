# Reskinner Plugin for PySimpleGUI

[![Downloads](https://static.pepy.tech/personalized-badge/psg-reskinner?period=total&units=international_system&left_color=grey&right_color=yellowgreen&left_text=downloads)](https://pepy.tech/project/psg-reskinner)
[![GitHub issues](https://img.shields.io/github/issues/definite-d/psg_reskinner)](https://github.com/definite-d/psg_reskinner/issues)
![GitHub forks](https://img.shields.io/github/forks/definite-d/psg_reskinner?logo=github&style=flat)
[![GitHub stars](https://img.shields.io/github/stars/definite-d/psg_reskinner)](https://github.com/definite-d/psg_reskinner/stargazers)
![PyPi Version](https://img.shields.io/pypi/v/psg-reskinner?style=flat)
![Python Versions](https://img.shields.io/pypi/pyversions/psg-reskinner.svg?style=flat&logo=python])
![License](https://img.shields.io/pypi/l/psg-reskinner.svg?style=flat&version=latest)

````shell
pip install PSG-Reskinner
````

<p align="center"> 
    <img src="https://github.com/definite-d/psg_reskinner/blob/main/res/demo.gif">
</p>

## What's Reskinner?

Reskinner is a Python 3 plugin for PySimpleGUI's Tkinter port which enables changing the theme of a PySimpleGUI window on the fly without the need for re-instantiating the window.

Please consider starring the project if you find it useful.

## Example Usage (Demo)

```python
# Reskinner Version 2.3.13
from psg_reskinner import animated_reskin, __version__
from PySimpleGUI import Window, Text, Button, Push, Titlebar, theme, theme_list, LOOK_AND_FEEL_TABLE
from random import choice as rc

right_click_menu = ['', [['Hi', ['Next Level', ['Deeper Level', ['a', 'b', 'c']], 'Hoho']], 'There']]

window_layout = [
    [Titlebar('Reskinner Demo')],
    [Text('Hello!', font=('Helvetica', 20))],
    [Text('You are currently running Reskinner instead of importing it.')],
    [Text('The theme of this window changes every 2 seconds.')],
    [Text('Changing to:')],
    [Button('DarkBlue3', k='current_theme', font=('Helvetica', 16), right_click_menu=right_click_menu)],
    [Text(f'Reskinner v{__version__}', font=('Helvetica', 8), pad=(0, 0)), Push()],
]

window = Window('Reskinner Demo', window_layout, element_justification='center', keep_on_top=True)

def _reskin_job():
    themes = theme_list()
    themes.remove(theme())
    new = rc(themes)
    window['current_theme'].update(new)
    animated_reskin(
        window=window,
        new_theme=new,
        theme_function=theme,
        lf_table=LOOK_AND_FEEL_TABLE,
    )
    window.TKroot.after(2000, _reskin_job)

started = False

while True:

    e, v = window.read(timeout=2000)

    if e in (None, 'Exit'):
        window.Close()
        break

    if not started:
        _reskin_job()
        started = True

```

## How does it work?

Reskinner runs through each element in a window, then by relying on the `element.widget` interface to access the underlying Tkinter object, it applies style changes to the window.

## What's the story behind psg_reskinner?
Like [Unda](https://github.com/definite-d/unda), I created Reskinner to be a part/feature of a desktop application which I'm developing, however, I decided to open-source it, as I imagined other developers would find such functionality useful in their projects as well.

Development began on Monday 15th August 2022.

## Why is it called Reskinner?
I didn't want it to go against the built-in conventions of `theme` and `look_and_feel` that PySimpleGUI has.

## Standards
Reskinner is:

 - [X] built using Python 3.7 (in PyCharm),

 - [X] fully PEP-8 compliant,

 - [X] distributed under the OSI-Approved MIT License.
