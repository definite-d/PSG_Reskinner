# Reskinner Plugin for PySimpleGUI

[![Downloads](https://static.pepy.tech/personalized-badge/psg-reskinner?period=total&units=international_system&left_color=grey&right_color=green&left_text=Downloads)](https://pepy.tech/project/psg-reskinner)
[![GitHub issues](https://img.shields.io/github/issues/definite-d/psg_reskinner)](https://github.com/definite-d/psg_reskinner/issues)
![GitHub forks](https://img.shields.io/github/forks/definite-d/psg_reskinner?logo=github&style=flat)
[![GitHub stars](https://img.shields.io/github/stars/definite-d/psg_reskinner)](https://github.com/definite-d/psg_reskinner/stargazers)
![PyPi Version](https://img.shields.io/pypi/v/psg-reskinner?style=flat)
![Python Versions](https://img.shields.io/pypi/pyversions/psg-reskinner.svg?style=flat&logo=python])
![License](https://img.shields.io/pypi/l/psg-reskinner.svg?style=flat&version=latest)

````text
pip install PSG-Reskinner
````

![Demo GIF](https://github.com/definite-d/psg_reskinner/blob/main/res/demo.gif)

## What's Reskinner?
Reskinner is a Python 3 plugin for PySimpleGUI's Tkinter port which enables changing the theme of a PySimpleGUI window on the fly without the need for re-instantiating the window.

## Example Usage (Demo)

```python
    from PSG_Reskinner import reskin
    from PySimpleGUI import Window, Text, Button, DropDown, theme_list, TIMEOUT_KEY

    window_layout = [
        [Text('Hello! You are currently running Reskinner instead of importing it.')],
        [Text('Clicking the button will change the theme to the one specified.')],
        [Text('Or do nothing. The theme will change every few seconds')],
        [DropDown(values=theme_list(), default_value='DarkBlue3', k='new_theme')],
        [Button('Change Theme', k='change')]
    ]

    window = Window('Reskinner Demo', window_layout, element_justification='center')

    while True:

        e, v = window.Read(timeout=3000)

        if e in (None, 'Exit'):
            window.Close()
            break

        if e == 'change':
            reskin(window, v['new_theme'])

        elif e == TIMEOUT_KEY:
            reskin(window)
``` 

## How does it work?

Reskinner runs through each element in a window, then by relying on the `Element.Widget` interface to access the underlying Tkinter object, it applies style changes to the window.

## What's the story behind psg_reskinner?
Like [Unda](https://github.com/definite-d/unda), I created Reskinner to be a part/feature of a desktop application which I'm developing, however, I decided to open-source it, as I imagined other developers would find such functionality useful in their projects as well.

Development began on Monday 15th August 2022.

## Why is it called Reskinner?
I didn't want it to conflict with the built-in conventions of `theme` and `look_and_feel` that PySimpleGUI has.

## Standards
Reskinner is:

 -[X] built using Python 3.7 (in PyCharm),

 -[X] fully PEP-8 compliant,

 -[X] distributed under the OSI-Approved MIT License.