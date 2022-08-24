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

__version__ = '1.1.3'

from PySimpleGUI import Window, theme_text_color, theme_slider_color, theme_progress_bar_color, theme_list, \
    theme_button_color, theme_background_color, theme_input_background_color, theme, theme_input_text_color, \
    theme_text_element_background_color
from random import choice as rc
from tkinter.ttk import Style

NON_GENERIC_ELEMENTS = ['progress', 'tabgroup', 'table', 'tree', 'button', 'text', 'multiline', 'listbox', 'spin']


def _check_if_generics_apply(element_name: str) -> bool:
    """
    Internal use only.

    Checks if a given element should undergo the generic config tweaks.

    If the element affected by the non-generic elements blacklist, it returns False.

    :param element_name: The name of the element
    :return: bool
    """
    valid = True
    for case in NON_GENERIC_ELEMENTS:
        if case in element_name:
            # print(element_name)
            valid = False
            break
    return valid


def reskin(window: Window, new_theme: str = None, exempt_element_keys: list = None) -> None:
    """
    Applies the theme instantaneously to the specified window.

    Do note that you still need to call 'theme()' after this from your code. That will ensure future windows start with
    the new theme, and it maintains the window transparency feature.

    :param window: The PySimpleGUI window to work on.
    :param new_theme: The name of the new theme to change to. Leaving this blank will use a random built-in theme.
    :param exempt_element_keys: A list of element keys which will be exempt from the theme change.
    :return: None
    """
    # Handle parameters
    ''' print(f'New theme: {new_theme}') '''
    new_theme = new_theme if new_theme is not None else rc(theme_list())
    exempt_element_keys = exempt_element_keys if exempt_element_keys is not None else []

    # Keep a few values of the old theme to crosscheck for customized elements.
    # old_theme = theme()  # This guy isn't being used right now.
    old_theme_background_color = theme_background_color()
    old_theme_button_color = theme_button_color()
    old_theme_text_color = theme_text_color()

    # Apply the new theme and re-color the window
    theme(new_theme)
    window.TKroot.config(background=theme_background_color())

    # Per-element changes happen henceforth
    for element in window.element_list():
        if element.Key not in exempt_element_keys:
            # Generic tweaks
            el = str(type(element)).lower()[0:len(str(type(element)).lower()) - 2].rsplit('.', 1)[1]
            element.ParentRowFrame.config(background=theme_background_color())
            if _check_if_generics_apply(el):
                element.Widget.configure(background=theme_background_color())
            # Element-specific tweaks
            if el == 'text':
                text_fg = element.Widget.cget('foreground')
                text_bg = element.Widget.cget('background')
                if text_fg == old_theme_text_color:
                    element.Widget.configure(foreground=theme_text_color()),
                    element.TextColor = theme_text_color()
                if text_bg == old_theme_background_color:
                    element.Widget.configure(background=theme_text_element_background_color())
            elif el in ('input', 'multiline'):
                element.Widget.configure(foreground=theme_input_text_color(), background=theme_input_background_color())
            elif el == 'listbox':
                element.Widget.configure(foreground=theme_input_text_color(),
                                         background=theme_input_background_color(),
                                         selectforeground=theme_input_background_color(),
                                         selectbackground=theme_input_text_color())
            elif el == 'slider':
                element.Widget.configure(foreground=theme_text_color(), troughcolor=theme_slider_color())
            elif el == 'button' and element.ButtonColor == old_theme_button_color:
                element.ButtonColor = theme_button_color()
                # For regular Tk buttons
                if 'ttk' not in str(type(element.TKButton)).lower():
                    element.Widget.configure(background=theme_button_color()[1], foreground=theme_button_color()[0],
                                             activebackground=theme_button_color()[0],
                                             activeforeground=theme_button_color()[1]
                                             )
                # For Ttk Buttons
                else:
                    style_name = element.Widget.cget('style')
                    styler = Style()
                    styler.configure(f'{style_name}', background=theme_button_color()[1],
                                     foreground=theme_button_color()[0])
                    styler.map(style_name,
                               foreground=[
                                   ('pressed', theme_button_color()[1]),
                                   ('active', theme_button_color()[1])
                               ],
                               background=[
                                   ('pressed', theme_button_color()[0]),
                                   ('active', theme_button_color()[0])
                               ]
                               )
            elif el == 'progressbar':
                style_name = element.TKProgressBar.style_name
                styler = Style()
                styler.configure(style_name, background=theme_progress_bar_color()[1],
                                 troughcolor=theme_progress_bar_color()[0])
            elif el == 'buttonmenu':
                element.Widget.configure(background=theme_button_color()[1], foreground=theme_button_color()[0],
                                         activebackground=theme_button_color()[0],
                                         activeforeground=theme_button_color()[1])
                element.TKMenu.configure(background=theme_input_background_color(), foreground=theme_input_text_color())
                menudef = element.MenuDefinition
                element.BackgroundColor = theme_input_background_color()
                element.TextColor = theme_input_text_color()
                element.update(menu_definition=menudef)

            elif el in 'spin':
                element.Widget.configure(background=theme_input_background_color(),
                                         foreground=theme_input_text_color(),
                                         buttonbackground=theme_input_background_color())
            elif el in ('combo', 'dropdown'):
                style_name = element.Widget.cget('style')
                styler = Style()
                styler.configure(style_name,
                                 selectforeground=theme_input_text_color(),
                                 selectbackground=theme_input_background_color(),
                                 selectcolor=theme_input_text_color(),
                                 fieldbackground=theme_input_background_color(),
                                 foreground=theme_input_text_color(),
                                 background=theme_button_color()[1],
                                 arrowcolor=theme_button_color()[0])
            elif el in ('table', 'tree'):
                style_name = element.Widget.cget('style')
                styler = Style()
                styler.configure(style_name, foreground=theme_text_color(), background=theme_background_color(),
                                 fieldbackground=theme_background_color(), fieldcolor=theme_text_color())
                styler.configure(f'{style_name}.Heading', foreground=theme_input_text_color(),
                                 background=theme_input_background_color())
            elif el in ('radio', 'checkbox'):
                from PySimpleGUI import _hex_to_hsl, _hsl_to_rgb, rgb
                text_hsl = _hex_to_hsl(theme_text_color())
                background_hsl = _hex_to_hsl(theme_background_color())
                l_delta = abs(text_hsl[2] - background_hsl[2]) / 10
                if text_hsl[2] > background_hsl[2]:
                    bg_rbg = _hsl_to_rgb(background_hsl[0], background_hsl[1], background_hsl[2] - l_delta)
                else:
                    bg_rbg = _hsl_to_rgb(background_hsl[0], background_hsl[1], background_hsl[2] + l_delta)
                toggle = rgb(*bg_rbg)
                element.Widget.configure(background=theme_background_color(), foreground=theme_text_color(),
                                         selectcolor=toggle,
                                         activebackground=theme_background_color(), activeforeground=theme_text_color())
            elif el == 'tabgroup':
                style_name = element.Widget.cget('style')
                styler = Style()
                print(styler.configure(style_name + '.Tab'))
                styler.configure(f'{style_name}', background=theme_background_color())
                styler.configure(f'{style_name}.Tab',
                                 background=theme_input_background_color(),
                                 foreground=theme_input_text_color())
                styler.map(f'{style_name}.Tab',
                           foreground=[
                               ('pressed', theme_button_color()[1]),
                               ('selected', theme_button_color()[0])
                           ],
                           background=[
                               ('pressed', theme_button_color()[0]),
                               ('selected', theme_background_color())
                           ]
                           )
        else:
            pass
    window.Refresh()


def main():

    from PySimpleGUI import Text, Button, DropDown, TIMEOUT_KEY

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


if __name__ == '__main__':
    main()
