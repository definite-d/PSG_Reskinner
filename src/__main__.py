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

# IMPORTS
from _tkinter import TclError
from colour import COLOR_NAME_TO_RGB, Color
from datetime import datetime as dt, timedelta
from PySimpleGUI.PySimpleGUI import COLOR_SYSTEM_DEFAULT, LOOK_AND_FEEL_TABLE, TITLEBAR_CLOSE_KEY, \
    TITLEBAR_DO_NOT_USE_AN_ICON, TITLEBAR_IMAGE_KEY, TITLEBAR_MAXIMIZE_KEY, TITLEBAR_METADATA_MARKER, \
    TITLEBAR_MINIMIZE_KEY, TITLEBAR_TEXT_KEY, Window, _hex_to_hsl, _hsl_to_rgb, rgb, theme, theme_add_new, \
    theme_background_color, theme_button_color, theme_input_background_color, theme_input_text_color, \
    theme_progress_bar_color, theme_slider_color, theme_text_color, theme_text_element_background_color, \
    ttk_part_mapping_dict
from random import choice as rc
from tkinter.ttk import Style
from typing import Callable, Dict, Union
from warnings import warn

# VERSIONING
__version__: str = '2.3.5'


# DEPRECATIION TRIGGER
if __version__.startswith('2.4'):
    m = 'Hello! Annoying little reminder to remove the deprecated functions, and this message.'
    raise Exception(m)


# CONSTANTS
NON_GENERIC_ELEMENTS = [
    'progressbar',
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
RGB_INTERPOLATION = 'rgb'
HUE_INTERPOLATION = 'hue'
HSL_INTERPOLATION = 'hsv'
ALTER_MENU_ACTIVE_COLORS = True


# ERROR CLASS
class ReskinnerException(Exception):
    def __init__(self, message):
        """
        Basic Exception class.

        First available from v2.2.0.
        :param message:
        """
        super().__init__(message)


# UTILITY FUNCTIONS
def _check_if_generics_apply(element_name: str) -> bool:

    """
    Internal use only.

    Checks if a given element should undergo the generic config tweaks.

    If the element affected by the non-generic elements blacklist, it returns False.

    First available from v1.1.3.
    :param element_name: The name of the element
    :return: bool
    """
    if element_name in NON_GENERIC_ELEMENTS:
        return False
    return True


def _reverse_dict(input_dict: dict) -> dict:
    """
    Deprecated from version 2.3.5; it will be removed entirely by the next minor release.

    Internal use only.

    Takes in a dict and returns a copy of it with the places of its keys and values swapped.

    First available from v2.0.34.
    :param input_dict: The source dictionary.
    :return: dict
    """
    warn('"_reverse_dict" has been deprecated from version 2.3.5; '
         'it will be removed entirely by the next minor release.')
    result = {str(key): value for key, value in list(input_dict.items())}
    return result


def _configure_ttk_scrollbar_style(style_name: str, styler: Style, new_theme_dict: Dict) -> None:
    """
    Internal use only.

    Gets the colors that would be used to create a ttk scrollbar based on how it's done in the PySimpleGUI source.

    First available from v2.0.34.
    :return: None
    """
    mapper = {'Background Color': new_theme_dict['BACKGROUND'],
              'Button Background Color': new_theme_dict['BUTTON'][1],
              'Button Text Color': new_theme_dict['BUTTON'][0],
              'Input Element Background Color': new_theme_dict['INPUT'],
              'Input Element Text Color': new_theme_dict['TEXT_INPUT'],
              'Text Color': new_theme_dict['TEXT'],
              'Slider Color': new_theme_dict['SCROLL']}

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

    First available from v2.2.0.

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
    Deprecated from version 2.3.5; it will be removed entirely by the next minor release.

    Internal use only.

    Takes a single dict as input, flattens a copy of it so that its values have no container types and returns that one.

    First available from v2.2.0.

    :param input_dict: The source dict.
    :param separator: A character used for indicating containers' children.
    :return: The flattened dict.
    """
    warn('"_flatten_dict" has been deprecated from version 2.3.5; '
         'it will be removed entirely by the next minor release.')
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

    First available from v2.2.0.

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


def _calculate_checkbox_or_radio_color(background_color: str, text_color: str) -> str:
    """
    Internal use only.

    Normally in PySimpleGUI, the color of checkboxes and radios is calculated based on the background color, so this
    function is meant to do a similar calculation that gives the exact same result that PySimpleGUI would give.

    First available from v2.3.4

    :param background_color: The bg of the element.
    :param text_color: Similar to `background_color`.
    :return: A web-format color string
    """
    # PySimpleGUI's color conversion functions give different results than those of the colour module, so I can't use
    # the color module's functionality for everything here.
    background_color = background_color if background_color.startswith('#') else Color(background_color).get_hex()
    text_color = text_color if text_color.startswith('#') else Color(text_color).get_hex()
    base_hsl = _hex_to_hsl(background_color)
    text_hsl = _hex_to_hsl(text_color)
    l_delta = abs(text_hsl[2] - base_hsl[2]) / 10 * (1 if text_hsl[2] < base_hsl[2] else -1)
    rgb_ = _hsl_to_rgb(base_hsl[0], base_hsl[1], base_hsl[2] + l_delta)
    result = rgb(*rgb_)
    return result


def _interpolate_colors(
        start: str,
        end: str,
        progress: float,
        interpolation_mode: Union[
            RGB_INTERPOLATION,
            HUE_INTERPOLATION,
            HSL_INTERPOLATION
        ] = RGB_INTERPOLATION, ) -> str:
    """
    Internal use only.

    Performs an interpolation calculation between two colors (start and end) and returns a Color object as the result.
    Inspired by https://www.alanzucconi.com/2016/01/06/colour-interpolation/ .

    RGB interpolation is simple lerping through RGB color space.
    Hue interpolation is lerping through HSL color space but moving only forward on the hue scale until it reaches the
    end color.
    HSV interpolation also lerps across HSL color space but it takes the shortest route to get to the end color.

    * "lerp" means "linear-interpolation", in case you didn't know.

    Each interpolation mode has a different visual effect which may look better than the others in certain scenarios.

    First available from v2.3.4.

    :param start: The starting color.
    :param end: The end color.
    :param progress: A float representing the current point in the interpolation where 0 marks the beginning and 1 marks
    the end.
    :param mode: The method to use for the interpolation calculation. Defaults to RGB interpolation.
    :return: A web-format color string representing the result of the calculation.
    """
    result = Color()
    start = Color(start)
    end = Color(end)
    if interpolation_mode == RGB_INTERPOLATION:
        result.set_red((start.get_red() + ((end.get_red() - start.get_red()) * progress)))
        result.set_green((start.get_green() + ((end.get_green() - start.get_green()) * progress)))
        result.set_blue((start.get_blue() + ((end.get_blue() - start.get_blue()) * progress)))
    elif interpolation_mode == HUE_INTERPOLATION:
        result.set_hue((start.get_hue() + ((end.get_hue() - start.get_hue()) * progress)))
        result.set_saturation((start.get_saturation() + ((end.get_saturation() - start.get_saturation()) * progress)))
        result.set_luminance((start.get_luminance() + ((end.get_luminance() - start.get_luminance()) * progress)))
    elif interpolation_mode == HSL_INTERPOLATION:
        if start.get_hue() > end.get_hue():
            start_ = start
            start = end
            end = start_
            del start_
            progress = 1 - progress
        diff = end.get_hue() - start.get_hue()
        if diff > 0.5:
            hue = ((start.get_hue() + 1) + progress * (end.get_hue() - (start.get_hue() + 1))) % 1
        else:
            hue = start.get_hue() + progress * diff
        result.set_hue(hue)
        result.set_saturation((start.get_saturation() + ((end.get_saturation() - start.get_saturation()) * progress)))
        result.set_luminance((start.get_luminance() + ((end.get_luminance() - start.get_luminance()) * progress)))

    return result.get_web()


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
        reskin_background: bool = True
) -> None:
    """
    Applies the theme instantaneously to the specified window. This is where the magic happens.

    First available from v1.0.0.

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
    :param reskin_background: True by default. If `True`, the window's background will be affected.
    :return: None
    """
    # Handle parameters
    if target_element_keys is not None and exempt_element_keys is not None:
        raise (ReskinnerException('Target elements and Exempt elements can\'t both be specified.'))
    whitelist = [element.key for element in window.element_list()]
    if target_element_keys or exempt_element_keys:
        whitelist = target_element_keys if target_element_keys else \
            [key for key in whitelist if key not in exempt_element_keys]

    if window not in list(WINDOW_THEME_MAP.keys()):
        WINDOW_THEME_MAP[window] = (theme_function(), lf_table[theme_function()])

    # Old theme stuff
    old_theme, old_theme_dict = WINDOW_THEME_MAP[window]

    # New theme stuff
    new_theme_dict = lf_table[new_theme].copy()

    # Window level changes
    if reskin_background:
        window.TKroot.config(background=new_theme_dict['BACKGROUND'])

    # Per-element changes happen henceforth
    for element in window.element_list():
        if element.key in whitelist:
            # Generic tweaks
            el = str(type(element)).lower()[:-2].rsplit('.', 1)[1]
            '''print(el)'''
            if element.ParentRowFrame:
                element.ParentRowFrame.configure(background=new_theme_dict['BACKGROUND'])
            if _check_if_generics_apply(el):
                element.widget.configure(background=new_theme_dict['BACKGROUND'])

            # Element-specific tweaks
            styler = Style()  # Declare a styler object

            # Right Click Menus (thanks for pointing this out @dwelden!)
            if element.TKRightClickMenu:
                element.ParentForm.right_click_menu_background_color = new_theme_dict['INPUT']
                element.ParentForm.right_click_menu_text_color = new_theme_dict['TEXT_INPUT']
                element.ParentForm.right_click_menu_disabled_color = DISABLED_COLOR
                element.ParentForm.right_click_menu_selected_colors = (
                    new_theme_dict['INPUT'], new_theme_dict['TEXT_INPUT']
                )
                element.set_right_click_menu(element.RightClickMenu)
                # We were never here...
                element.ParentForm.right_click_menu_background_color = old_theme_dict['INPUT']
                element.ParentForm.right_click_menu_text_color = old_theme_dict['TEXT_INPUT']
                element.ParentForm.right_click_menu_disabled_color = DISABLED_COLOR
                element.ParentForm.right_click_menu_selected_colors = (
                    old_theme_dict['INPUT'], old_theme_dict['TEXT_INPUT']
                )

            # Handling ttk scrollbars
            if element.hsb_style_name:
                _configure_ttk_scrollbar_style(element.hsb_style_name, styler, new_theme_dict)
            if element.vsb_style_name:
                _configure_ttk_scrollbar_style(element.vsb_style_name, styler, new_theme_dict)

            # Custom Titlebar ___________________________________________________________________________________
            # Container Columns. A little duck-type hack is used to identify the expanded column.
            if (TITLEBAR_METADATA_MARKER == getattr(element, 'metadata')) or \
                    (getattr(element, 'Grab', False) and getattr(element, 'expand_x', False) and el == 'column'):
                element.widget.configure(background=new_theme_dict['BUTTON'][1])
                if element.ParentRowFrame is not None:
                    element.ParentRowFrame.configure(background=new_theme_dict['BUTTON'][1])
            # Title
            if (element.key in [
                TITLEBAR_TEXT_KEY,
                TITLEBAR_MAXIMIZE_KEY,
                TITLEBAR_MINIMIZE_KEY,
                TITLEBAR_CLOSE_KEY,
            ]) or (TITLEBAR_DO_NOT_USE_AN_ICON and element.key == TITLEBAR_IMAGE_KEY):
                element.widget.configure(foreground=new_theme_dict['BUTTON'][0], background=new_theme_dict['BUTTON'][1])
                if element.ParentRowFrame is not None:
                    element.ParentRowFrame.configure(background=new_theme_dict['BUTTON'][1])

            # Other elements
            if el == 'column' and element.Scrollable:
                    element.TKColFrame.canvas.config(background=new_theme_dict['BACKGROUND'])
                    element.TKColFrame.TKFrame.config(background=new_theme_dict['BACKGROUND'])

            if el in ('text', 'statusbar'):
                text_fg = element.widget.cget('foreground')
                text_bg = element.widget.cget('background')
                if _check_for_honors(text_fg, old_theme_dict['TEXT'], honor_previous):
                    element.widget.configure(foreground=new_theme_dict['TEXT']),
                    element.TextColor = new_theme_dict['TEXT']
                if _check_for_honors(text_bg, old_theme_dict['BACKGROUND'], honor_previous):
                    element.widget.configure(background=new_theme_dict['BACKGROUND'])
            elif el in ('horizontalseparator', 'verticalseparator'):
                style_name = element.widget.cget('style')
                styler.configure(style_name, background=new_theme_dict['BACKGROUND'])
            elif el == 'frame':
                element.widget.configure(foreground=new_theme_dict['TEXT'])
            elif el == 'menu':
                element.BackgroundColor = new_theme_dict['INPUT']
                element.TextColor = new_theme_dict['TEXT_INPUT']
                menudef = getattr(element, 'MenuDefinition')
                element.update(menu_definition=menudef)
            elif el == 'sizegrip':
                sizegrip_style = element.widget.cget('style')
                styler.configure(sizegrip_style, background=new_theme_dict['BACKGROUND'])
            elif el == 'optionmenu':
                element.widget['menu'].configure(foreground=new_theme_dict['TEXT_INPUT'],
                                                 background=new_theme_dict['INPUT'], )
                if ALTER_MENU_ACTIVE_COLORS:
                    element.widget['menu'].configure(
                        activeforeground=new_theme_dict['INPUT'],
                        activebackground=new_theme_dict['TEXT_INPUT'],
                    )
                element.widget.configure(foreground=new_theme_dict['TEXT_INPUT'],
                                         background=new_theme_dict['INPUT'], )
                # activeforeground=new_theme_dict['INPUT'],
                # activebackground=new_theme_dict['TEXT_INPUT'])
            elif el in ('input', 'multiline'):
                element.widget.configure(foreground=new_theme_dict['TEXT_INPUT'],
                                         background=new_theme_dict['INPUT'],
                                         selectforeground=new_theme_dict['INPUT'],
                                         selectbackground=new_theme_dict['TEXT_INPUT'])
            elif el == 'listbox':
                element.widget.configure(foreground=new_theme_dict['TEXT_INPUT'],
                                         background=new_theme_dict['INPUT'],
                                         selectforeground=new_theme_dict['INPUT'],
                                         selectbackground=new_theme_dict['TEXT_INPUT'])
            elif el == 'slider':
                element.widget.configure(foreground=new_theme_dict['TEXT'], troughcolor=new_theme_dict['SCROLL'])
            elif el == 'button':
                element.ButtonColor = new_theme_dict['BUTTON']
                # For regular Tk buttons
                if 'ttk' not in str(type(getattr(element, 'TKButton'))).lower():
                    element.widget.configure(background=new_theme_dict['BUTTON'][1],
                                             foreground=new_theme_dict['BUTTON'][0],
                                             activebackground=new_theme_dict['BUTTON'][0],
                                             activeforeground=new_theme_dict['BUTTON'][1]
                                             )
                # For Ttk Buttons
                else:
                    style_name = element.widget.cget('style')
                    styler.configure(f'{style_name}', background=new_theme_dict['BUTTON'][1],
                                     foreground=new_theme_dict['BUTTON'][0])
                    styler.map(style_name,
                               foreground=[
                                   ('pressed', new_theme_dict['BUTTON'][1]),
                                   ('active', new_theme_dict['BUTTON'][1])
                               ],
                               background=[
                                   ('pressed', new_theme_dict['BUTTON'][0]),
                                   ('active', new_theme_dict['BUTTON'][0])
                               ]
                               )
            elif el == 'progressbar':
                style_name = getattr(element, 'TKProgressBar').style_name
                styler.configure(style_name, background=new_theme_dict['PROGRESS'][1],
                                 troughcolor=new_theme_dict['PROGRESS'][0])
            elif el == 'buttonmenu':
                menudef = getattr(element, 'MenuDefinition')
                element.BackgroundColor = new_theme_dict['INPUT']
                element.TextColor = new_theme_dict['TEXT_INPUT']
                element.widget.configure(
                    background=new_theme_dict['BUTTON'][1],
                    foreground=new_theme_dict['BUTTON'][0]
                )
                element.update(menu_definition=menudef)
                # We were never here.
                element.BackgroundColor = old_theme_dict['INPUT']
                element.TextColor = old_theme_dict['TEXT_INPUT']
            elif el in 'spin':
                element.widget.configure(background=new_theme_dict['INPUT'],
                                         foreground=new_theme_dict['TEXT_INPUT'],
                                         buttonbackground=new_theme_dict['INPUT'])
            elif el == 'combo':
                # Configuring the listbox of the combo.
                prefix = '$popdown.f.l configure'
                window.TKroot.tk.call('eval', f'set popdown [ttk::combobox::PopdownWindow {element.widget}]')
                window.TKroot.tk.call('eval', f"{prefix} -background {new_theme_dict['INPUT']}")
                window.TKroot.tk.call('eval', f"{prefix} -foreground {new_theme_dict['TEXT_INPUT']}")
                window.TKroot.tk.call('eval', f"{prefix} -selectforeground {new_theme_dict['INPUT']}")
                window.TKroot.tk.call('eval', f"{prefix} -selectbackground {new_theme_dict['TEXT_INPUT']}")
                style_name = element.widget.cget('style')
                # Configuring the combo itself.
                styler.configure(style_name,
                                 selectforeground=new_theme_dict['INPUT'],
                                 selectbackground=new_theme_dict['TEXT_INPUT'],
                                 selectcolor=new_theme_dict['TEXT_INPUT'],
                                 fieldbackground=new_theme_dict['INPUT'],
                                 foreground=new_theme_dict['TEXT_INPUT'],
                                 background=new_theme_dict['BUTTON'][1],
                                 arrowcolor=new_theme_dict['BUTTON'][0],
                                 )
                styler.map(style_name,
                           foreground=[
                               ('readonly', new_theme_dict['TEXT_INPUT']),
                               ('disabled', DISABLED_COLOR)
                           ],
                           fieldbackground=[
                               ('readonly', new_theme_dict['INPUT'])
                           ]
                           )
            elif el in ('table', 'tree'):
                style_name = element.widget.cget('style')
                styler.configure(style_name, foreground=new_theme_dict['TEXT'], background=new_theme_dict['BACKGROUND'],
                                 fieldbackground=new_theme_dict['BACKGROUND'], fieldcolor=new_theme_dict['TEXT'])
                styler.map(style_name, foreground=[('selected', new_theme_dict['BUTTON'][0])],
                           background=[('selected', new_theme_dict['BUTTON'][1])])
                styler.configure(f'{style_name}.Heading', foreground=new_theme_dict['TEXT_INPUT'],
                                 background=new_theme_dict['INPUT'])
            elif el in ('radio', 'checkbox'):
                toggle = _calculate_checkbox_or_radio_color(new_theme_dict['BACKGROUND'], new_theme_dict['TEXT'])
                element.widget.configure(background=new_theme_dict['BACKGROUND'], foreground=new_theme_dict['TEXT'],
                                         selectcolor=toggle,
                                         activebackground=new_theme_dict['BACKGROUND'],
                                         activeforeground=new_theme_dict['TEXT'])
            elif el == 'tabgroup':
                style_name = element.widget.cget('style')
                styler.configure(f'{style_name}', background=new_theme_dict['BACKGROUND'])
                styler.configure(f'{style_name}.Tab',
                                 background=new_theme_dict['INPUT'],
                                 foreground=new_theme_dict['TEXT_INPUT'])
                styler.map(f'{style_name}.Tab',
                           foreground=[
                               ('pressed', new_theme_dict['BUTTON'][1]),
                               ('selected', new_theme_dict['TEXT'])
                           ],
                           background=[
                               ('pressed', new_theme_dict['BUTTON'][0]),
                               ('selected', new_theme_dict['BACKGROUND'])
                           ]
                           )
        else:
            pass
    WINDOW_THEME_MAP[window] = (new_theme, new_theme_dict)
    if set_future:
        theme_function(new_theme)
    window.Refresh()


def animated_reskin(
        window: Window,
        new_theme: str,
        theme_function: Callable,
        lf_table: dict,
        duration: int = 3000,
        interpolation_mode: Union[
            RGB_INTERPOLATION,
            HUE_INTERPOLATION,
            HSL_INTERPOLATION
        ] = RGB_INTERPOLATION,
        set_future: bool = False,
        exempt_element_keys: list = None,
        target_element_keys: list = None,
        honor_previous: bool = True,
        reskin_background: bool = True
):
    """
    Does exactly the same job as the Reskin function, but gives a gradual animated change between colors.

    The future is here :) .

    First available from v2.2.0.
    The `interpolation_mode` argument was added in v2.3.4.

    Keyword args
    :param window: The window to work on.
    :param new_theme: The name of the new theme, as you would pass it to your `theme()` call.
    :param theme_function: The PySimpleGUI `theme()` function object itself. Pass it without parentheses.
    :param lf_table: The `LOOK_AND_FEEL_TABLE` constant from your PySimpleGUI import.
    :param duration: Amount of time in milliseconds to spend for the entire animation. Defaults to 3000 milliseconds.
    :param interpolation_mode: The method to use for interpolation between colors. Defaults to RGB_INTERPOLATION. See
    the documentation for `_interpolate_colors()` for more on interpolation.
    :param set_future: False by default. If `True`, future windows will also use the new theme.
    :param exempt_element_keys: A list of element keys which will be excluded from the process if specified. Cannot be
    used alongside `target_element_keys`.
    :param target_element_keys: A list of element keys which will be the only elements used in the process if specified.
    Cannot be used alongside `exempt_element_keys`.
    :param honor_previous: True by default. If `True`, Reskinner will only change a value if it wasn't set
    to a custom one.
    :param reskin_background: True by default. If `True`, the window's background will be affected.
    :return: None
    """
    """
    Welcome, fellow programmer (or future self). These comments are meant to explain what's going on in the process 
    behind the animation. 
    """
    if window not in list(WINDOW_THEME_MAP.keys()):
        WINDOW_THEME_MAP[window] = (theme_function(), lf_table[theme_function()])
    old_themedict = WINDOW_THEME_MAP[window][1]
    new_themedict = lf_table[new_theme]
    # print(WINDOW_THEME_MAP[window][0], new_theme, theme_function())
    # micro = float(str(timedelta(milliseconds=duration)).rsplit(':', 1)[1])
    call_time = dt.now()
    end_time = call_time + timedelta(milliseconds=duration)
    colors = {}
    """
    Here, we break down the themedict so there are no containers (e.g. the BUTTON entry), and store the result in the 
    colors variable, using {key}___@{index} to denote container types.
    
    Hence `'BUTTON': ('#asdf', '#123456')` will become `'BUTTON___@0': '#asdf'` and `'BUTTON___@1':'#123456'`.
    """
    for key in old_themedict:
        if key in new_themedict:
            if isinstance(old_themedict[key], str) \
                    and (old_themedict[key].startswith('#') or old_themedict[key] in COLOR_NAME_TO_RGB):
                end = new_themedict[key]
                start = old_themedict[key]
                colors[key] = (start, end)
            if isinstance(old_themedict[key], tuple):
                for pos, col in enumerate(old_themedict[key]):
                    if isinstance(col, str) \
                            and (col.startswith('#') or col in COLOR_NAME_TO_RGB):
                        try:
                            end = new_themedict[key][pos]
                        except IndexError:
                            continue
                        start = col
                        colors[f'{key}___@{pos}'] = (start, end)
    """
    This section is where the linear color interpolation happens. The formula (per constituent of color space e.g. RGB) 
    for interpolation from color a to color b at any given point (t) in the interpolation is:
    
        a + (b - a) * t
        
    In our case, t (which is the progress of the animation at that point) will represented by:
        duration since the start of the animation / duration of the entire animation = delta
        
    Sorry for the funny type-manipulation going on, but basically:
     
        delta = (float(str((dt.now() - call_time)).rsplit(':', 1)[1]) * 1000) / duration
    
    ...means the exact same thing as t.
    """
    try:
        while dt.now() <= end_time:
            interdict: dict = new_themedict.copy()
            delta = (float(str((dt.now() - call_time)).rsplit(':', 1)[1]) * 1000) / duration
            for k, (a, b) in colors.items():
                try:
                    current: str = _interpolate_colors(a, b, delta, interpolation_mode)
                except ValueError:
                    continue
                if '___@' not in k:  # Nice and simple; a single-color theme entry.
                    interdict[k] = current
                    continue
                else:  # A tuple-style theme entry. The intermediary themedict uses lists instead.
                    k, pos = k.split('___@')
                    interdict[k] = [] if not isinstance(interdict[k], list) else interdict[k]
                    interdict[k].insert(int(pos), current)

            # Temporarily rename the current point to the destination.
            lf_table[new_theme] = interdict
            try:
                reskin(window, new_theme, theme_function, LOOK_AND_FEEL_TABLE, set_future,
                       exempt_element_keys, target_element_keys, honor_previous, reskin_background)
            except TclError:  # The window has been closed.
                pass
        """
        End of animation reached.
        
        Due to smaller, more precise time-based delta (duration progress per frame) increments, and the condition for 
        checking if the animation should end being based on (ultimately imprecise) time comparisons, delta never actually 
        reaches 1, hence the interpolation will not end exactly at the new theme's colors (the destination). 
        
        Rather, it will end at a value as close as the time comparison permits (which is extremely close to the actual 
        destination), then skip to the destination itself.
          
        The effect of the skip is almost unnoticeable, and the end user probably wouldn't even know, but it's there ;).
        
        Hope that explains the animation process.
        """
        lf_table[new_theme] = new_themedict
        try:
            reskin(window, new_theme, theme_function, lf_table, set_future, exempt_element_keys,
                   target_element_keys, honor_previous, reskin_background)
        except TclError:  # The window has been closed.
            pass

    except Exception as e:
        # Basically provide more context to whatever error occurs.
        print(f'While trying to perform an animated reskin from {WINDOW_THEME_MAP[window][0]} to {new_theme}, an exception occurred:')
        raise e


def toggle_transparency(window: Window) -> None:
    """
    Use this function to toggle background transparency on or off. Works with reskinned and non-reskinned windows.

    First available from v2.0.34.

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
    """
    Main Function.

    Gets called when the module is run instead of imported.

    First available from v1.0.0.
    """
    # from psg_reskinner import reskin, animated_reskin, __version__
    from PySimpleGUI import Window, Text, Button, Push, Titlebar, theme_list, theme, LOOK_AND_FEEL_TABLE, TIMEOUT_KEY
    # from random import choice as rc

    rmenu = ['', ['Hi', 'There']]

    window_layout = [
        [Titlebar('Reskinner Demo')],
        [Text('Hello!', font=('Helvetica', 20))],
        [Text('You are currently running Reskinner instead of importing it.')],
        [Text('The theme of this window changes every 3 seconds.')],
        [Text('Changing to:')],
        [Button('DarkBlue3', k='ctheme', font=('Helvetica', 16), right_click_menu=rmenu)],
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
                            lf_table=LOOK_AND_FEEL_TABLE, )


# ENTRY POINT
if __name__ == '__main__':
    main()
