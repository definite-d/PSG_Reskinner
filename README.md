# Reskinner Plugin for PySimpleGUI

````text
pip install PSG-Reskinner
````

https://github.com/definite-d/psg_reskinner.

## What's Reskinner?
Reskinner is a Python 3 plugin for PySimpleGUI's Tkinter port which enables changing the theme of a PySimpleGUI window on the fly without the need for re-instantiating the window.

## Example Usage (Demo)

```python
import PySimpleGUI as sg
from PSG_Reskinner import reskin

window_layout = [
        [sg.Text('Hello! You are currently running Reskinner instead of importing it.')],
        [sg.Text('Clicking the button will change the theme to the one specified.')],
        [sg.Text('Or do nothing. The theme will change every few seconds')],
        [sg.DropDown(values=sg.theme_list(), default_value='DarkBlue3', k='new_theme')],
        [sg.Button('Change Theme', k='change')],
    ]

    window = sg.Window('Reskinner Demo', window_layout, element_justification='center')

    while True:

        e, v = window.Read(timeout=3000)

        if e in (None, 'Exit'):
            window.Close()
            break

        if e == 'change':
            reskin(window, v['new_theme'])

        else:
            reskin(window, rc(sg.theme_list()))
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

 * lightweight (about 4KB in size)

 * built using Python 3.7 (in PyCharm),

 * fully PEP-8 compliant,

 * distributed under the OSI-Approved MIT License.