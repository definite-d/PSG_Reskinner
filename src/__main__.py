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


# VERSIONING
__version__ = '2.2.12'


# IMPORTS
from PySimpleGUI.PySimpleGUI import Window, theme_text_color, theme_slider_color, theme_progress_bar_color, \
    theme_button_color, theme_background_color, theme_input_background_color, theme, theme_input_text_color, \
    theme_text_element_background_color, theme_add_new, ttk_part_mapping_dict, _rgb_to_hsl, \
    LOOK_AND_FEEL_TABLE, COLOR_SYSTEM_DEFAULT, TITLEBAR_METADATA_MARKER, TITLEBAR_TEXT_KEY, TITLEBAR_IMAGE_KEY, \
    TITLEBAR_MINIMIZE_KEY, TITLEBAR_MAXIMIZE_KEY, TITLEBAR_CLOSE_KEY, TITLEBAR_DO_NOT_USE_AN_ICON
from colour import web2rgb, hsl2web, Color, COLOR_NAME_TO_RGB
from datetime import timedelta, datetime as dt
from random import choice as rc
from _tkinter import TclError
from tkinter.ttk import Style
from typing import Callable, Union


# CONSTANTS
NON_GENERIC_ELEMENTS = [
    'progress',
    'tabgroup',
    'table',
    'tree',
    'button',
    'text',
    'multiline',
    'listbox',
    'spin',
    'horizontalseparator',
    'verticalseparator',
    'sizegrip',
]
WINDOW_THEME_MAP = {}
DISABLED_COLOR = '#A3A3A3'
ALTER_MENU_ACTIVE_COLORS = True


# ERROR CLASS
class ReskinnerException(Exception):
    def __init__(self, message):
        super().__init__(message)


# UTILITY FUNCTIONS
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
            valid = False
            break
    return valid


def _reverse_dict(input_dict: dict) -> dict:
    """
    Internal use only.

    Takes in a dict and returns a copy of it with the places of its keys and values swapped.

    :param input_dict: The source dictionary.
    :return: dict
    """
    result = {str(key): value for key, value in list(input_dict.items())}
    return result


def _configure_ttk_scrollbar_style(style_name: str, styler: Style) -> None:
    """
    Internal use only.
    
    Gets the colors that would be used to create a ttk scrollbar based on how it's done in the PySimpleGUI source.

    :return: None
    """
    mapper = {'Background Color': theme_background_color(),
              'Button Background Color': theme_button_color()[1],
              'Button Text Color': theme_button_color()[0],
              'Input Element Background Color': theme_input_background_color(),
              'Input Element Text Color': theme_input_text_color(),
              'Text Color': theme_text_color(),
              'Slider Color': theme_slider_color()}

    trough_color = mapper[ttk_part_mapping_dict['Trough Color']]
    frame_color = mapper[ttk_part_mapping_dict['Frame Color']]
    background_color = mapper[ttk_part_mapping_dict['Background Color']]
    arrow_color = mapper[ttk_part_mapping_dict['Arrow Button Arrow Color']]

    styler.configure(style_name, troughcolor=trough_color, framecolor=frame_color, bordercolor=frame_color)
    styler.map(style_name,
               background=[("selected", background_color), ('active', arrow_color), ('background', background_color),
                           ('!focus', background_color)])
    styler.map(style_name, arrowcolor=[("selected", arrow_color), ('active', background_color),
                                       ('background', background_color), ('!focus', arrow_color)])


def _check_for_honors(current_value: Union[str, int], check_value: Union[str, int], honor_previous: bool) -> bool:
    """
    Internal use only.

    Used as a lazy shortcut function to conduct `honor_previous` checks.

    :param current_value: The current value to check
    :param check_value: The reference to check against for differences.
    Usually the corresponding value of the `current_value` from the old theme.
    :param honor_previous: The honor previous boolean.
    :return:
    """
    if (not honor_previous) or (honor_previous and current_value == check_value):
        return True


def _flatten_dict(input_dict: dict, separator='_') -> dict:
    """
    Internal use only.

    Takes a single dict as input, flattens a copy of it so that its values have no container types and returns that one.

    :param input_dict: The source dict.
    :param separator: A character used for indicating containers' children.
    :return: The flattened dict.
    """
    source = input_dict.copy()
    flat = {}
    for (key, value) in source.items():
        if isinstance(value, (list, tuple)):
            for n, x in enumerate(value):
                flat[f'{str(key)}{separator}{n}'] = x
        # elif isinstance(value, (str, int)):
        else:
            flat[key] = value
    return flat


def _safe_theme_list(lf_table) -> list:
    """
    Internal use only.

    Finds a list of themes that won't give a Tkinter TclError.

    :param lf_table: The look and feel table regarding your theme list.
    :return: Error free list of themes.
    """
    safe_list = []
    previous_theme = theme()
    for each_theme in lf_table.keys():
        if COLOR_SYSTEM_DEFAULT in lf_table[each_theme].values():
            continue
        try:
            theme(each_theme)
        except TclError:
            continue
        safe_list.append(each_theme)
    theme(previous_theme)
    return safe_list


# RESKIN AND UTILITY FUNCTIONS
def reskin(
        window: Window,
        new_theme: str,
        theme_function: Callable,
        lf_table: dict,
        set_future: bool = False,
        exempt_element_keys: list = None,
        target_element_keys: list = None,
        honor_previous: bool = True,
) -> None:
    """
    Applies the theme instantaneously to the specified window. This is where the magic happens.

    :param window: The window to work on.
    :param new_theme: The name of the new theme, as you would pass it to your `theme()` call.
    :param theme_function: The PySimpleGUI `theme()` function object itself. Pass it without parentheses.
    :param lf_table: The `LOOK_AND_FEEL_TABLE` constant from your PySimpleGUI import.
    :param set_future: False by default. If `True`, future windows will also use the new theme.
    :param exempt_element_keys: A list of element keys which will be excluded from the process if specified. Cannot be
    used alongside `target_element_keys`.
    :param target_element_keys: A list of element keys which will be the only elements used in the process if specified.
    Cannot be used alongside `exempt_element_keys`.
    :param honor_previous: True by default. If `True`, Reskinner will only change a value if it wasn't set
    to a custom one.
    :return: None
    """
    # scope_theme = theme()
    # Handle parameters
    new_theme = new_theme if new_theme is not None else rc(lf_table)
    exempt_element_keys = exempt_element_keys if exempt_element_keys is not None else []
    if target_element_keys is not None and exempt_element_keys is not None:
        raise (ReskinnerException('Target elements and Exempt elements can\'t both be specified.'))

    if window not in list(WINDOW_THEME_MAP.keys()):
        WINDOW_THEME_MAP[window] = (theme_function(), lf_table[theme_function()])

    # Old theme stuff
    old_theme, old_theme_dict = WINDOW_THEME_MAP[window]
    # rev_old_theme_dict = _reverse_dict(old_theme_dict)

    # New theme stuff
    new_theme_dict = lf_table[new_theme]
    theme_add_new(new_theme, new_theme_dict)
    theme(new_theme)
    # rev_new_theme_dict = _reverse_dict(new_theme_dict)

    # Window level changes
    window.TKroot.config(background=theme_background_color())

    # Per-element changes happen henceforth
    for element in window.element_list():
        if (element.Key not in exempt_element_keys) or (element.Key in target_element_keys):

            # Generic tweaks
            el = str(type(element)).lower()[0:len(str(type(element)).lower()) - 2].rsplit('.', 1)[1]
            '''print(el)'''
            if element.ParentRowFrame is not None:
                element.ParentRowFrame.configure(background=theme_background_color())
            if _check_if_generics_apply(el):
                element.Widget.configure(background=theme_background_color())

            # Element-specific tweaks
            styler = Style()  # Declare a styler object

            # Handling ttk scrollbars
            orientations = ['Vertical', 'Horizontal']
            for i in range(window._counter_for_ttk_widgets):
                for orientation in orientations:
                    style_name = f'{i + 1}___{element.Key}.{orientation}.TScrollbar'
                    if styler.configure(style_name) is not None:  # If we've stumbled upon a valid style:
                        _configure_ttk_scrollbar_style(style_name, styler)

            # Custom Titlebar ___________________________________________________________________________________
            # Container Columns. A little duck-type hack is used to identify the expanded column.
            if (element.metadata == TITLEBAR_METADATA_MARKER) or \
                    (getattr(element, 'Grab', False) and getattr(element, 'expand_x', False) and el == 'column'):
                element.Widget.configure(background=theme_button_color()[1])
                if element.ParentRowFrame is not None:
                    element.ParentRowFrame.configure(background=theme_button_color()[1])
            # Title
            if (element.key in [
                TITLEBAR_TEXT_KEY,
                TITLEBAR_MAXIMIZE_KEY,
                TITLEBAR_MINIMIZE_KEY,
                TITLEBAR_CLOSE_KEY,
            ]) or (TITLEBAR_DO_NOT_USE_AN_ICON and element.key == TITLEBAR_IMAGE_KEY):
                element.Widget.configure(foreground=theme_button_color()[0], background=theme_button_color()[1])
                if element.ParentRowFrame is not None:
                    element.ParentRowFrame.configure(background=theme_button_color()[1])

            # Other elements
            if el in ('text', 'statusbar'):
                text_fg = element.Widget.cget('foreground')
                text_bg = element.Widget.cget('background')
                if _check_for_honors(text_fg, old_theme_dict['TEXT'], honor_previous):
                    element.Widget.configure(foreground=theme_text_color()),
                    element.TextColor = theme_text_color()
                if _check_for_honors(text_bg, old_theme_dict['BACKGROUND'], honor_previous):
                    element.Widget.configure(background=theme_text_element_background_color())
            elif el == 'frame':
                element.Widget.configure(foreground=theme_text_color())
            elif el == 'menu':
                element.BackgroundColor = theme_input_background_color()
                element.TextColor = theme_input_text_color()
                menudef = getattr(element, 'MenuDefinition')
                element.update(menu_definition=menudef)
            elif el == 'sizegrip':
                sizegrip_style = element.Widget.cget('style')
                styler.configure(sizegrip_style, background=theme_background_color())
            elif el == 'optionmenu':
                element.Widget['menu'].configure(foreground=theme_input_text_color(),
                                                 background=theme_input_background_color(),)
                if ALTER_MENU_ACTIVE_COLORS:
                    element.Widget['menu'].configure(
                                                 activeforeground=theme_input_background_color(),
                                                 activebackground=theme_input_text_color(),
                    )
                element.Widget.configure(foreground=theme_input_text_color(),
                                         background=theme_input_background_color(),
                                         activeforeground=theme_input_background_color(),
                                         activebackground=theme_input_text_color())
            elif el in ('input', 'multiline'):
                element.Widget.configure(foreground=theme_input_text_color(),
                                         background=theme_input_background_color(),
                                         selectforeground=theme_input_background_color(),
                                         selectbackground=theme_input_text_color())
            elif el == 'listbox':
                element.Widget.configure(foreground=theme_input_text_color(),
                                         background=theme_input_background_color(),
                                         selectforeground=theme_input_background_color(),
                                         selectbackground=theme_input_text_color())
            elif el == 'slider':
                element.Widget.configure(foreground=theme_text_color(), troughcolor=theme_slider_color())
            elif el == 'button':
                element.ButtonColor = theme_button_color()
                # For regular Tk buttons
                if 'ttk' not in str(type(getattr(element, 'TKButton'))).lower():
                    element.Widget.configure(background=theme_button_color()[1], foreground=theme_button_color()[0],
                                             activebackground=theme_button_color()[0],
                                             activeforeground=theme_button_color()[1]
                                             )
                # For Ttk Buttons
                else:
                    style_name = element.Widget.cget('style')
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
                style_name = getattr(element, 'TKProgressBar').style_name
                styler.configure(style_name, background=theme_progress_bar_color()[1],
                                 troughcolor=theme_progress_bar_color()[0])
            elif el == 'buttonmenu':
                menudef = getattr(element, 'MenuDefinition')
                element.BackgroundColor = theme_input_background_color()
                element.TextColor = theme_input_text_color()
                element.update(menu_definition=menudef)

            elif el in 'spin':
                element.Widget.configure(background=theme_input_background_color(),
                                         foreground=theme_input_text_color(),
                                         buttonbackground=theme_input_background_color())
            elif el == 'combo':
                # Configuring the listbox of the combo.
                prefix = '$popdown.f.l configure'
                window.TKroot.tk.call('eval', f'set popdown [ttk::combobox::PopdownWindow {element.Widget}]')
                window.TKroot.tk.call('eval', f'{prefix} -background {theme_input_background_color()}')
                window.TKroot.tk.call('eval', f'{prefix} -foreground {theme_input_text_color()}')
                window.TKroot.tk.call('eval', f'{prefix} -selectforeground {theme_input_background_color()}')
                window.TKroot.tk.call('eval', f'{prefix} -selectbackground {theme_input_text_color()}')
                style_name = element.Widget.cget('style')
                # Configuring the combo itself.
                styler.configure(style_name,
                                 selectforeground=theme_input_background_color(),
                                 selectbackground=theme_input_text_color(),
                                 selectcolor=theme_input_text_color(),
                                 fieldbackground=theme_input_background_color(),
                                 foreground=theme_input_text_color(),
                                 background=theme_button_color()[1],
                                 arrowcolor=theme_button_color()[0],
                                 )
                styler.map(style_name,
                           foreground=[
                               ('readonly', theme_input_text_color()),
                               ('disabled', DISABLED_COLOR)
                           ],
                           fieldbackground=[
                               ('readonly', theme_input_background_color())
                           ]
                           )
            elif el in ('table', 'tree'):
                style_name = element.Widget.cget('style')
                styler.configure(style_name, foreground=theme_text_color(), background=theme_background_color(),
                                 fieldbackground=theme_background_color(), fieldcolor=theme_text_color())
                styler.map(style_name, foreground=[('selected', theme_button_color()[0])],
                           background=[('selected', theme_button_color()[1])])
                styler.configure(f'{style_name}.Heading', foreground=theme_input_text_color(),
                                 background=theme_input_background_color())
            elif el in ('radio', 'checkbox'):
                t_r, t_g, t_b = web2rgb(theme_text_color())
                b_r, b_g, b_b = web2rgb(theme_background_color())
                text_hsl = _rgb_to_hsl(t_r, t_g, t_b)
                background_hsl = _rgb_to_hsl(b_r, b_g, b_b)
                l_delta = abs(text_hsl[2] - background_hsl[2]) / 50
                if text_hsl[2] > background_hsl[2]:
                    adjusted = l_delta - background_hsl[2] if l_delta - background_hsl[2] >= 0 else 0
                    toggle = hsl2web((background_hsl[0], background_hsl[1], adjusted))
                else:
                    adjusted = l_delta + background_hsl[2] if l_delta + background_hsl[2] <= 1 else 1
                    toggle = hsl2web((background_hsl[0], background_hsl[1], adjusted))
                element.Widget.configure(background=theme_background_color(), foreground=theme_text_color(),
                                         selectcolor=toggle,
                                         activebackground=theme_background_color(), activeforeground=theme_text_color())
            elif el == 'tabgroup':
                style_name = element.Widget.cget('style')
                styler.configure(f'{style_name}', background=theme_background_color())
                styler.configure(f'{style_name}.Tab',
                                 background=theme_input_background_color(),
                                 foreground=theme_input_text_color())
                styler.map(f'{style_name}.Tab',
                           foreground=[
                               ('pressed', theme_button_color()[1]),
                               ('selected', theme_text_color())
                           ],
                           background=[
                               ('pressed', theme_button_color()[0]),
                               ('selected', theme_background_color())
                           ]
                           )
        else:
            pass

    WINDOW_THEME_MAP[window] = (new_theme, new_theme_dict)
    if set_future:
        theme_function(new_theme)
    window.Refresh()
    # theme(scope_theme)


def animated_reskin(
        window: Window,
        new_theme: str,
        theme_function: Callable,
        lf_table: dict,
        duration: int = 3000,
        set_future: bool = False,
        exempt_element_keys: list = None,
        target_element_keys: list = None,
        honor_previous: bool = True,
):
    """
    Does exactly the same job as the Reskin function, but gives a gradual animated change between colors.

    The future is here :) .

    Keyword args
    :param window: The window to work on.
    :param new_theme: The name of the new theme, as you would pass it to your `theme()` call.
    :param theme_function: The PySimpleGUI `theme()` function object itself. Pass it without parentheses.
    :param lf_table: The `LOOK_AND_FEEL_TABLE` constant from your PySimpleGUI import.
    :param duration: Amount of time in milliseconds to spend for the entire animation. Defaults to 3000 milliseconds.
    :param set_future: False by default. If `True`, future windows will also use the new theme.
    :param exempt_element_keys: A list of element keys which will be excluded from the process if specified. Cannot be
    used alongside `target_element_keys`.
    :param target_element_keys: A list of element keys which will be the only elements used in the process if specified.
    Cannot be used alongside `exempt_element_keys`.
    :param honor_previous: True by default. If `True`, Reskinner will only change a value if it wasn't set
    to a custom one.
    :return: None
    """
    old_themedict = lf_table[theme_function()]
    new_themedict = lf_table[new_theme]
    # micro = float(str(timedelta(milliseconds=duration)).rsplit(':', 1)[1])
    call_time = dt.now()
    end_time = call_time + timedelta(milliseconds=duration)
    colors = {}
    for key in old_themedict:
        if key in new_themedict:
            if isinstance(old_themedict[key], str) \
                    and (old_themedict[key].startswith('#') or old_themedict[key] in COLOR_NAME_TO_RGB):
                end = Color(new_themedict[key])
                start = Color(old_themedict[key])
                colors[key] = (start, end)
            if isinstance(old_themedict[key], tuple) or isinstance(old_themedict[key], list):
                for pos, col in enumerate(old_themedict[key]):
                    if isinstance(col, str) \
                            and (col.startswith('#') or col in COLOR_NAME_TO_RGB):
                        try:
                            end = Color(new_themedict[key][pos])
                        except IndexError:
                            continue
                        start = Color(col)
                        colors[f'{key}___@{pos}'] = (start, end)
    while dt.now() <= end_time:
        interdict: dict = new_themedict.copy()
        delta = (float(str((dt.now()-call_time)).rsplit(':', 1)[1])*1000)/duration
        for k, (a, b) in colors.items():
            try:
                current = Color()
                current.set_red((a.get_red() + ((b.get_red()-a.get_red()) * delta)))
                current.set_green((a.get_green() + ((b.get_green()-a.get_green()) * delta)))
                current.set_blue((a.get_blue() + ((b.get_blue()-a.get_blue()) * delta)))
            except ValueError:
                continue
            if '___@' not in k:  # Nice and simple; a single-color theme entry.
                interdict[k] = current.get_hex()
                continue
            else:  # A tuple-style theme entry. The intermediary themedict uses lists instead.
                k, pos = k.split('___@')
                interdict[k] = [] if not isinstance(interdict[k], list) else interdict[k]
                interdict[k].insert(int(pos), current.get_hex())
        lf_table[f'___{new_theme}@reskinneranimation'] = interdict
        try:
            reskin(window, f'___{new_theme}@reskinneranimation', theme_function, lf_table, set_future,
                   exempt_element_keys, target_element_keys, honor_previous)
        except TclError:  # The window has been closed.
            pass
    try:
        reskin(window, new_theme, theme_function, lf_table, set_future, exempt_element_keys,
               target_element_keys, honor_previous)
    except TclError:  # The window has been closed.
        pass
    del lf_table[f'___{new_theme}@reskinneranimation']


def toggle_transparency(window: Window) -> None:
    """
    Use this function to toggle background transparency on or off. Works with reskinned and non-reskinned windows.

    :param window: The window to work on.
    :return: None
    """
    window_bg = window.TKroot.cget('background')
    transparent_color = window.TKroot.attributes('-transparentcolor')
    window.set_transparent_color(window_bg if transparent_color == '' else '')


# MAIN FUNCTION


# Required because certain themes currently cause this error:
#   _tkinter.TclError: unknown color name "1234567890"
safethemes = _safe_theme_list(LOOK_AND_FEEL_TABLE)


def main():
    # from psg_reskinner import reskin, animated_reskin, __version__
    # from random import choice as rc
    from PySimpleGUI import Window, Text, Button, Push, Titlebar, theme, LOOK_AND_FEEL_TABLE, TIMEOUT_KEY

    window_layout = [
        [Titlebar('Reskinner Demo')],
        [Text('Hello!', font=('Helvetica', 20))],
        [Text('You are currently running Reskinner instead of importing it.')],
        [Text('The theme of this window changes every 3 seconds.')],
        [Text('Changing to:')],
        [Button('DarkBlue3', k='ctheme', font=('Helvetica', 16))],
        [Text(f'Reskinner v{__version__}', font=('Helvetica', 8), pad=(0, 0)), Push()],
    ]

    window = Window('Reskinner Demo', window_layout, element_justification='center')

    while True:

        e, v = window.Read(timeout=2000)

        if e in (None, 'Exit'):
            window.Close()
            break

        elif e == TIMEOUT_KEY:
            '''reskin(window, rc(theme_list()), theme, LOOK_AND_FEEL_TABLE)'''
            new = rc(safethemes)
            window['ctheme'].update(new)
            animated_reskin(window=window,
                            new_theme=new,
                            theme_function=theme,
                            lf_table=LOOK_AND_FEEL_TABLE)


# ENTRY POINT
if __name__ == '__main__':
    main()
