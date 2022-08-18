"""
PySimpleGUI Reskinner Plugin

https://github.com/definite_d/psg_reskinner/
Enables changing the theme of a PySimpleGUI window on the fly without the need for re-instantiating the window

Copyright (c) 2022 Divine Afam-Ifediogor

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__version__ = '1.0.0'

from PySimpleGUI import Window, theme_text_color, theme_slider_color, theme_progress_bar_color, Text, theme_list, \
    theme_button_color, Button, theme_background_color, theme_input_background_color, theme, theme_input_text_color, \
    DropDown, theme_text_element_background_color


def reskin(window: Window, new_theme: str, future: bool = True) -> None:
    """
    Applies the theme instantaneously to the specified window.
    :param window: The PySimpleGUI window to work on.
    :param new_theme: The name of the new theme to change to.
    :param future: If set to False, it sets the theme for
                   the given window only; future windows will stick to the old theme.
    :return: None
    """
    old_theme = theme()
    theme(new_theme)
    window.TKroot.config(background=theme_background_color())
    for element in window.element_list():
        element.Widget.config(background=theme_background_color())
        element.ParentRowFrame.config(background=theme_background_color())
        if 'text' in str(type(element)).lower():
            element.Widget.config(foreground=theme_text_color())
            element.Widget.config(background=theme_text_element_background_color())
        if 'input' in str(type(element)).lower():
            element.Widget.config(foreground=theme_input_text_color())
            element.Widget.config(background=theme_input_background_color())
        if 'progress' in str(type(element)).lower():
            element.Widget.config(foreground=theme_progress_bar_color()[0])
            element.Widget.config(background=theme_progress_bar_color()[1])
        if 'slider' in str(type(element)).lower():
            element.Widget.config(foreground=theme_slider_color())
        if 'button' in str(type(element)).lower():
            element.Widget.config(foreground=theme_button_color()[0])
            element.Widget.config(background=theme_button_color()[1])
    window.Refresh()
    if not future:
        theme(old_theme)


def main():
    from random import choice as rc

    window_layout = [
        [Text('Hello! You are currently running Reskinner instead of importing it.')],
        [Text('Clicking the button will change the theme to the one specified.')],
        [Text('Or do nothing. The theme will change every few seconds')],
        [DropDown(values=theme_list(), default_value='DarkBlue3', k='new_theme')],
        [Button('Change Theme', k='change')],
    ]

    window = Window('Reskinner Demo', window_layout, element_justification='center')

    while True:

        e, v = window.Read(timeout=3000)

        if e in (None, 'Exit'):
            window.Close()
            break

        if e == 'change':
            reskin(window, v['new_theme'])

        else:
            reskin(window, rc(theme_list()))


if __name__ == '__main__':
    main()
