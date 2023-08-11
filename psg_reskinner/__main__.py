"""
PySimpleGUI Reskinner Plugin

https://github.com/definite_d/psg_reskinner/

Enables changing the theme of a PySimpleGUI window on the fly without the need for re-instantiating the window

Copyright (c) 2023 Divine Afam-Ifediogor

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
from datetime import datetime as dt, timedelta
from tkinter import Menu as TKMenu, Widget
from tkinter.ttk import Style
from typing import Callable, Dict, Union
from warnings import warn

from PySimpleGUI.PySimpleGUI import COLOR_SYSTEM_DEFAULT, DEFAULT_PROGRESS_BAR_COLOR_OFFICIAL, \
    DEFAULT_PROGRESS_BAR_COMPUTE, LOOK_AND_FEEL_TABLE, TITLEBAR_METADATA_MARKER, Window, _hex_to_hsl, _hsl_to_rgb, \
    rgb, ttk_part_mapping_dict
from colour import COLOR_NAME_TO_RGB, Color

# VERSIONING
__version__: str = '2.3.13'

# DEPRECATION TRIGGER
if __version__.startswith('2.4'):
    m = 'Hello! Annoying little reminder to remove the deprecated functions, and this message.'
    raise Exception(m)

# CONSTANTS
NON_GENERIC_ELEMENTS = [
    'button',
    'horizontalseparator',
    'listbox',
    'multiline',
    'progressbar',
    'sizegrip',
    'spin',
    'tabgroup',
    'table',
    'text',
    'tree',
    'verticalseparator'
]

WINDOW_THEME_MAP = {}
DISABLED_COLOR = '#A3A3A3'
RGB_INTERPOLATION = 'rgb'
HUE_INTERPOLATION = 'hue'
HSL_INTERPOLATION = 'hsv'
ALTER_MENU_ACTIVE_COLORS = True
DEFAULT_ANIMATED_RESKIN_DURATION = 450


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
def _is_element_generic(element_name: str) -> bool:
    """
    Internal use only.

    Checks if a given element should undergo the generic config tweaks.

    If the element affected by the non-generic elements blacklist, it returns False.

    First available from v1.1.3.
    Renamed from `_check_if_generics_apply` to `_is_element_generic` in v2.3.12.
    :param element_name: The name of the element
    :return: bool
    """
    if element_name in NON_GENERIC_ELEMENTS:
        return False
    return True


def _reverse_dict(input_dict: dict) -> dict:
    """
    Deprecated from version 2.3.5; it will be removed entirely by the next minor release (version 2.4.x).

    Internal use only.

    Takes in a dict and returns a copy of it with the places of its keys and values swapped.

    First available from v2.0.34.
    :param input_dict: The source dictionary.
    :return: dict
    """
    warn('"_reverse_dict" has been deprecated from version 2.3.5; '
         'it will be removed entirely by the next minor release (version 2.4.x).')
    result = {str(key): value for key, value in list(input_dict.items())}
    return result


def _configure_ttk_scrollbar_style(
        style_name: str,
        styler: Style,
        new_theme_dict: Dict
) -> None:
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
               background=[
                   ("selected", background_color),
                   ('active', arrow_color),
                   ('background', background_color),
                   ('!focus', background_color)
               ])
    styler.map(style_name, arrowcolor=[
        ("selected", arrow_color),
        ('active', background_color),
        ('background', background_color),
        ('!focus', arrow_color)
    ])


def _check_for_honors(current_value: Union[str, int], check_value: Union[str, int], honor_previous: bool) -> bool:
    """
    Internal use only.

    Used as a lazy shortcut function to conduct `honor_previous` checks.

    If True, the element's previous color is preserved instead of changing it,
    hence "honoring" that color.

    First available from v2.2.0.

    :param current_value: The current value to check
    :param check_value: The reference to check against for differences.
    Usually the corresponding value of the `current_value` from the old theme.
    :param honor_previous: The honor previous boolean.
    :return:
    """

    if (not honor_previous) or (honor_previous and current_value == check_value):
        return True
    return False


def _flatten_dict(input_dict: dict, separator='_') -> dict:
    """
    Deprecated from version 2.3.5; it will be removed entirely by the next minor release (version 2.4.x).

    Internal use only.

    Takes a single dict as input, flattens a copy of it so that its values have no container types and returns that one.

    First available from v2.2.0.

    :param input_dict: The source dict.
    :param separator: A character used for indicating containers' children.
    :return: The flattened dict.
    """
    warn('"_flatten_dict" has been deprecated from version 2.3.5; '
         'it will be removed entirely by the next minor release (version 2.4.x).')
    source = input_dict.copy()
    flat = {}
    for (key, value) in source.items():
        if isinstance(value, (list, tuple)):
            for n, x in enumerate(value):
                flat[f'{str(key)}{separator}{n}'] = x
        else:
            flat[key] = value
    return flat


def _safe_theme_list(lf_table: Dict[str, Dict[str, str]]) -> list:
    """
    Internal use only.

    Finds a list of themes that won't give a Tkinter TclError.

    First available from v2.2.0.

    :param lf_table: The look and feel table regarding your theme list.
    :return: Error free list of themes.
    """
    safe_list = sorted(
        [
            each_theme
            for each_theme in lf_table.keys()
            if COLOR_SYSTEM_DEFAULT not in lf_table[each_theme].values()
        ]
    )
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

    - RGB interpolation is simple lerping through RGB color space.
    - Hue interpolation is lerping through HSL color space but moving only forward on the hue scale until it reaches the
        end color.
    - HSV interpolation also lerps across HSL color space, but it takes the shortest route to get to the end color.

    Note: "lerp" means "linear-interpolation", in case you didn't know.

    Each interpolation mode has a different visual effect which may look better than the others in certain scenarios.

    First available from v2.3.4.

    :param start: The starting color.
    :param end: The end color.
    :param progress: A float representing the current point in the interpolation where 0 marks the beginning and 1 marks
    the end.
    :param interpolation_mode: The method to use for the interpolation calculation. Defaults to RGB interpolation.
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


def _recurse_menu(tkmenu: Union[TKMenu, Widget], fg: Union[Color, str], bg: Union[Color, str]):
    """
    Internal use only.

    New and improved logic to change the theme of menus; we no longer take the lazy route of
    re-declaring new menu elements with each theme change - a method which Tkinter has an upper limit
    on. Rather, we recursively find and reconfigure the individual Menu objects that make up menus and
    submenus.

    First available from v2.3.7.

    :param tkmenu: The Tkinter menu object.
    :return: None
    """

    # This fixes issue #8. Thank you @richnanney!
    if tkmenu.index('end') is None:
        return

    for index in range(0, tkmenu.index('end') + 1):
        tkmenu.entryconfigure(
            index,
            background=bg,
            foreground=fg,
            activeforeground=bg,
            activebackground=fg,
        )
    for child in tkmenu.children.values():
        if issubclass(type(child), TKMenu):
            _recurse_menu(child, fg, bg)


# COLOR_SYSTEM_DEFAULT HANDLER
class _ColorSystemDefaultSieve:
    """
    Internal use only.

    Handles scenarios where the COLOR_SYSTEM_DEFAULT variable may be encountered.

    Thanks to @macdeport for first reporting it, and @richnanney for frankly making me think of a solution.
    This solves issues #1 and #7 once and for all.

    First available from v2.3.12.
    """
    def __init__(self, window: Window):
        self.window = window
        self._TK_COLORS = [
            'SystemButtonFace',
            'SystemButtonText',
            'SystemWindow',
            'SystemWindowText',
            'SystemScrollbar',
        ]
        self.TK_COLORS = {c: self._tk_colorname_to_color(c) for c in self._TK_COLORS}

        # This dict is used to emulate the themedict of what the GrayGrayGray theme (furthest you can get to default in
        # PySimpleGUI). However, because defaults go well beyond just the colors in a themedict (they get RESTRICTED to
        # themedicts when a theme is set), certain parts (such as the headers of Tables and scrollbars) may not be
        # exactly the same as what you would get with Tkinter-set defaults. For now, this is the next best thing that
        # can be called a solution to the Default problem. I'll still try to develop a better solution.
        self.DEFAULTS = {
            "BACKGROUND":   self.get_tkcolor('SystemButtonFace'),
            "TEXT":         self.get_tkcolor('SystemButtonText'),
            "INPUT":        self.get_tkcolor('SystemWindow'),
            "TEXT_INPUT":   self.get_tkcolor('SystemWindowText'),
            "SCROLL":       self.get_tkcolor('SystemScrollbar'),
            "BUTTON":       (self.get_tkcolor('SystemButtonText'), self.get_tkcolor('SystemButtonFace')),
            "PROGRESS":     DEFAULT_PROGRESS_BAR_COLOR_OFFICIAL,
        }

    def get_tkcolor(self, colorname):
        return self.TK_COLORS.get(colorname) or colorname

    def _tk_colorname_to_color(self, colorname):
        result = Color()
        result.set_rgb(tuple(x / 65535 for x in self.window.TKroot.winfo_rgb(colorname)))
        return result.get_hex_l()

    def _sieve_action(self, key, value):
        if value != COLOR_SYSTEM_DEFAULT:
            if isinstance(value, (tuple, list)):
                value = type(value)(map(
                    lambda index_and_sub_value:
                    self.get_tkcolor(index_and_sub_value[1]) if index_and_sub_value[1] != COLOR_SYSTEM_DEFAULT
                    else self.DEFAULTS[key][index_and_sub_value[0]],
                    enumerate(value)
                ))
            elif isinstance(value, str):
                value = self.get_tkcolor(value)
            return value
        else:
            return self.DEFAULTS[key]

    def sieve_themedict(self, themedict: Dict):
        return {key: self._sieve_action(key, value) for key, value in themedict.copy().items()}


# DEFAULT_PROGRESS_BAR_COMPUTE HANDLER
def _compute_progressbar(themedict: Dict, create_new_copy: bool = False):
    """
    Internal use only.

    Handles the DEFAULT_PROGRESS_BAR_COMPUTE scenario.

    First available from v2.3.12.
    """
    if themedict['PROGRESS'] == DEFAULT_PROGRESS_BAR_COMPUTE:
        themedict = themedict.copy() if create_new_copy else themedict
        if themedict['BUTTON'][1] != themedict['INPUT'] and themedict['BUTTON'][1] != themedict['BACKGROUND']:
            themedict['PROGRESS'] = (themedict['BUTTON'][1], themedict['INPUT'])
        else:
            themedict['PROGRESS'] = (themedict['TEXT_INPUT'], themedict['INPUT'])
    return themedict


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
    # Firstly, we add the window to the mapping of windows that we've encountered thus far.
    # This mapping is important because it enables us to obtain the previous theme programmatically
    # at all times, a feature required by Reskinner.
    if window not in list(WINDOW_THEME_MAP.keys()):
        WINDOW_THEME_MAP[window] = (theme_function(), lf_table[theme_function()])

    # Obtain the old and new theme names and themedicts.
    old_theme, old_theme_dict = WINDOW_THEME_MAP[window]
    new_theme_dict = lf_table[new_theme].copy()

    # Before going any further, we have enough info to disregard redundant calls, so we do so...
    if (new_theme == old_theme) and (new_theme_dict == old_theme_dict):
        return

    # COLOR_SYSTEM_DEFAULT Sieve
    _sieve = _ColorSystemDefaultSieve(window)
    old_theme_dict = _sieve.sieve_themedict(_compute_progressbar(old_theme_dict))
    new_theme_dict = _sieve.sieve_themedict(_compute_progressbar(new_theme_dict))

    # Handle parameters
    if target_element_keys is not None and exempt_element_keys is not None:
        raise (ReskinnerException('Target elements and Exempt elements can\'t both be specified.'))
    whitelist = [element.key for element in window.element_list()]
    if target_element_keys or exempt_element_keys:
        whitelist = target_element_keys if target_element_keys else \
            list(filter(lambda key: key not in exempt_element_keys, whitelist))

    # Window level changes
    if reskin_background:
        window.TKroot.configure(background=new_theme_dict['BACKGROUND'])

    titlebar_row_frame = 'Not Set'

    # Per-element changes happen henceforth
    for element in filter(lambda element: element.key in whitelist, window.element_list()):
        # Generic tweaks
        el = type(element).__name__.lower()
        '''print(el)'''
        if element.ParentRowFrame:
            element.ParentRowFrame.configure(background=new_theme_dict['BACKGROUND'])
        if _is_element_generic(el) \
                and _check_for_honors(
            element.widget.cget('background'),
            old_theme_dict['BACKGROUND'],
            honor_previous
        ):
            element.widget.configure(background=new_theme_dict['BACKGROUND'])

        # Declare a styler object.
        styler = Style()

        # Right Click Menus (thanks for pointing this out @dwelden!)
        if element.TKRightClickMenu:
            _recurse_menu(
                element.TKRightClickMenu,
                new_theme_dict['TEXT_INPUT'],
                new_theme_dict['INPUT']
            )

        # Handling ttk scrollbars
        element_style_name = getattr(element, 'ttk_style_name')
        if styler.configure(element_style_name) and ('TScrollbar' in element_style_name):
            if getattr(element, 'Scrollable', False):
                digit, rest = getattr(element, 'ttk_style_name').replace('Horizontal', 'Vertical').split('_', 1)
                digit = str(int(digit) - 1)
                vertical_style = f'{digit}_{rest}'
                _configure_ttk_scrollbar_style(vertical_style, styler, new_theme_dict)
            _configure_ttk_scrollbar_style(getattr(element, 'ttk_style_name'), styler, new_theme_dict)

        # Elements _________________________________________________________________________________________________
        # Custom Titlebar
        if element.metadata == TITLEBAR_METADATA_MARKER:
            element.widget.configure(background=new_theme_dict['BUTTON'][1])
            if element.ParentRowFrame is not None:
                element.ParentRowFrame.configure(background=new_theme_dict['BUTTON'][1])
            titlebar_row_frame = str(element.ParentRowFrame)
            continue

        # Titlebar elements
        if str(element.widget).startswith(titlebar_row_frame+'.'):
            element.ParentRowFrame.configure(background=new_theme_dict['BUTTON'][1])
            element.widget.configure(background=new_theme_dict['BUTTON'][1])
            if 'foreground' in element.widget.keys():
                element.widget.configure(foreground=new_theme_dict['BUTTON'][0])
            continue

        # Button
        if el == 'button':
            # For regular Tk buttons
            if 'ttk' not in str(type(getattr(element, 'TKButton'))).lower():
                element.widget.configure(
                    background=new_theme_dict['BUTTON'][1],
                    foreground=new_theme_dict['BUTTON'][0],
                    activebackground=new_theme_dict['BUTTON'][0],
                    activeforeground=new_theme_dict['BUTTON'][1]
                )
            # For Ttk Buttons
            else:
                style_name = element.widget.cget('style')
                styler.configure(
                    f'{style_name}',
                    background=new_theme_dict['BUTTON'][1],
                    foreground=new_theme_dict['BUTTON'][0]
                )
                styler.map(
                    style_name,
                    foreground=[
                        ('pressed', new_theme_dict['BUTTON'][1]),
                        ('active', new_theme_dict['BUTTON'][1])
                    ],
                    background=[
                        ('pressed', new_theme_dict['BUTTON'][0]),
                        ('active', new_theme_dict['BUTTON'][0])
                    ]
                )
                continue

        # ButtonMenu
        elif el == 'buttonmenu':
            element.widget.configure(
                background=new_theme_dict['BUTTON'][1],
                foreground=new_theme_dict['BUTTON'][0]
            )
            if hasattr(element, 'TKMenu'):
                _recurse_menu(element.TKMenu, fg=new_theme_dict['TEXT_INPUT'], bg=new_theme_dict['INPUT'])
            continue

        # Column (Scrollable)
        elif el == 'column' and hasattr(element, 'TKColFrame'):
            if hasattr(element.TKColFrame, 'canvas'):  # This means the column is scrollable.
                element.TKColFrame.canvas.configure(background=new_theme_dict['BACKGROUND'])
                element.TKColFrame.configure(background=new_theme_dict['BACKGROUND'])
                element.TKColFrame.canvas.children['!frame'].configure(
                    background=new_theme_dict['BACKGROUND']
                )
            continue

        # Combo
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
            styler.configure(
                style_name,
                selectforeground=new_theme_dict['INPUT'],
                selectbackground=new_theme_dict['TEXT_INPUT'],
                selectcolor=new_theme_dict['TEXT_INPUT'],
                fieldbackground=new_theme_dict['INPUT'],
                foreground=new_theme_dict['TEXT_INPUT'],
                background=new_theme_dict['BUTTON'][1],
                arrowcolor=new_theme_dict['BUTTON'][0],
            )
            styler.map(
                style_name,
                foreground=[
                    ('readonly', new_theme_dict['TEXT_INPUT']),
                    ('disabled', DISABLED_COLOR)
                ],
                fieldbackground=[
                    ('readonly', new_theme_dict['INPUT'])
                ]
            )
            continue

        # Frame
        elif el == 'frame':
            element.widget.configure(foreground=new_theme_dict['TEXT'])
            continue

        # Listbox
        elif el == 'listbox':
            element.widget.configure(
                foreground=new_theme_dict['TEXT_INPUT'],
                background=new_theme_dict['INPUT'],
                selectforeground=new_theme_dict['INPUT'],
                selectbackground=new_theme_dict['TEXT_INPUT']
            )
            continue

        # Menu
        elif el == 'menu':
            _recurse_menu(
                element.widget,
                new_theme_dict['TEXT_INPUT'],
                new_theme_dict['INPUT']
            )
            continue

        # OptionMenu
        elif el == 'optionmenu':
            element.widget['menu'].configure(foreground=new_theme_dict['TEXT_INPUT'],
                                             background=new_theme_dict['INPUT'], )
            if ALTER_MENU_ACTIVE_COLORS:
                element.widget['menu'].configure(
                    activeforeground=new_theme_dict['INPUT'],
                    activebackground=new_theme_dict['TEXT_INPUT'],
                )
            element.widget.configure(
                foreground=new_theme_dict['TEXT_INPUT'],
                background=new_theme_dict['INPUT'],
            )
            # activeforeground=new_theme_dict['INPUT'],
            # activebackground=new_theme_dict['TEXT_INPUT'])
            continue

        # ProgressBar
        elif el == 'progressbar':
            style_name = getattr(element, 'TKProgressBar').style_name
            styler.configure(
                style_name,
                background=new_theme_dict['PROGRESS'][0],
                troughcolor=new_theme_dict['PROGRESS'][1]
            )
            continue

        # Sizegrip
        elif el == 'sizegrip':
            sizegrip_style = element.widget.cget('style')
            styler.configure(sizegrip_style, background=new_theme_dict['BACKGROUND'])
            continue

        # Slider
        elif el == 'slider':
            element.widget.configure(
                foreground=new_theme_dict['TEXT'],
                troughcolor=new_theme_dict['SCROLL']
            )
            continue

        # Spin
        elif el in 'spin':
            element.widget.configure(
                background=new_theme_dict['INPUT'],
                foreground=new_theme_dict['TEXT_INPUT'],
                buttonbackground=new_theme_dict['INPUT']
            )
            continue

        # TabGroup
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
            continue

        # Checkbox, Radio
        elif el in ('checkbox', 'radio'):
            toggle = _calculate_checkbox_or_radio_color(new_theme_dict['BACKGROUND'], new_theme_dict['TEXT'])
            element.widget.configure(background=new_theme_dict['BACKGROUND'], foreground=new_theme_dict['TEXT'],
                                     selectcolor=toggle,
                                     activebackground=new_theme_dict['BACKGROUND'],
                                     activeforeground=new_theme_dict['TEXT'])
            continue

        # HorizontalSeparator, VerticalSeparator
        elif el in ('horizontalseparator', 'verticalseparator'):
            style_name = element.widget.cget('style')
            styler.configure(style_name, background=new_theme_dict['BACKGROUND'])
            continue

        # Input, Multiline
        elif el in ('input', 'multiline'):
            element.widget.configure(
                foreground=new_theme_dict['TEXT_INPUT'],
                background=new_theme_dict['INPUT'],
                selectforeground=new_theme_dict['INPUT'],
                selectbackground=new_theme_dict['TEXT_INPUT']
            )
            continue

        # StatusBar, Text
        elif el in ('statusbar', 'text'):
            text_fg = _sieve.get_tkcolor(element.widget.cget('foreground'))
            text_bg = _sieve.get_tkcolor(element.widget.cget('background'))
            if _check_for_honors(text_fg, old_theme_dict['TEXT'], honor_previous):
                element.widget.configure(foreground=new_theme_dict['TEXT']),
                element.TextColor = new_theme_dict['TEXT']
            if _check_for_honors(text_bg, old_theme_dict['BACKGROUND'], honor_previous):
                element.widget.configure(background=new_theme_dict['BACKGROUND'])
            continue

        # Table, Tree
        elif el in ('table', 'tree'):
            style_name = element.widget.cget('style')
            styler.configure(style_name, foreground=new_theme_dict['TEXT'], background=new_theme_dict['BACKGROUND'],
                             fieldbackground=new_theme_dict['BACKGROUND'], fieldcolor=new_theme_dict['TEXT'])
            styler.map(style_name, foreground=[('selected', new_theme_dict['BUTTON'][0])],
                       background=[('selected', new_theme_dict['BUTTON'][1])])
            styler.configure(f'{style_name}.Heading', foreground=new_theme_dict['TEXT_INPUT'],
                             background=new_theme_dict['INPUT'])
            continue

    WINDOW_THEME_MAP[window] = (new_theme, new_theme_dict)
    if set_future:
        theme_function(new_theme)
    window.Refresh()


def animated_reskin(
        window: Window,
        new_theme: str,
        theme_function: Callable,
        lf_table: dict,
        duration: int = DEFAULT_ANIMATED_RESKIN_DURATION,
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
    sieve = _ColorSystemDefaultSieve(window)
    old_themedict = WINDOW_THEME_MAP[window][1]
    old_themedict = sieve.sieve_themedict(_compute_progressbar(old_themedict.copy()))
    new_themedict = lf_table[new_theme]
    new_themedict = sieve.sieve_themedict(_compute_progressbar(new_themedict.copy()))
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
        checking if the animation should end being based on (ultimately imprecise) time comparisons, delta never 
        actually reaches 1, hence the interpolation will not end exactly at the new theme's colors (the destination). 

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
        print(
            f'While trying to perform an animated reskin from {WINDOW_THEME_MAP[window][0]} to {new_theme}, an '
            f'exception occurred:'
        )
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
def main():
    """
    Main Function.

    Gets called when the module is run instead of imported.

    First available from v1.0.0.
    """
    # % START DEMO % #
    # from psg_reskinner import animated_reskin, __version__
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
        themes = theme_list().copy()
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

    # % END DEMO % #
    return


# ENTRY POINT
if __name__ == '__main__':
    main()