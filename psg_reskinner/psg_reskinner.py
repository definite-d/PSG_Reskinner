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

#  PSG_Reskinner
#
#  Enables changing the themes of your PySimpleGUI windows and elements
#  instantaneously on the fly without the need for re-instantiating the window.
#
#  MIT License
#
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#
from datetime import datetime, timedelta
from tkinter import TclError
from tkinter.ttk import Style
from tkinter.ttk import Widget as TTKWidget
from typing import Callable, Optional, Union

from PySimpleGUI import (
    TITLEBAR_METADATA_MARKER,
    Checkbox,
    Column,
    Combo,
    Element,
    OptionMenu,
    ProgressBar,
    Radio,
    Table,
    Tree,
    Window,
)

from .colorprocessor import ColorProcessor
from .constants import (
    ALTER_MENU_ACTIVE_COLORS,
    DEFAULT_ANIMATED_RESKIN_DURATION,
    HSL_INTERPOLATION,
    HUE_INTERPOLATION,
    RGB_INTERPOLATION,
    WINDOW_THEME_MAP,
)
from .deprecation import deprecation_trigger
from .utilities import _lower_class_name
from .version import __version__

# DEPRECATION TRIGGER
deprecation_trigger()


# RESKIN AND UTILITY FUNCTIONS
def reskin(
    window: Window,
    new_theme: str,
    theme_function: Callable,
    lf_table: dict,
    set_future: bool = True,
    element_filter: Optional[Callable[[Element], bool]] = None,
    reskin_background: bool = True,
    **kwargs,
) -> None:
    """
    Applies the theme instantaneously to the specified window. This is where the magic happens.

    First available from v1.0.0.

    :param window: The window to operate on.
    :param new_theme: The theme to transition to.
    :param theme_function: The theme change function from PySimpleGUI within your code. Required because of namespaces.
    :param lf_table: The LOOK_AND_FEEL_TABLE from PySimpleGUI from within your code. The `new_theme` should be in there.
    :param set_future: If set to True, the `new_theme` will be applied to all future windows.
    :param element_filter: A callable of your choice that takes an element as its only parameter and returns True or
        False. Elements that result in True will be reskinned, and others will be skipped.
    :param reskin_background: If True, the background color of the window will be reskinned. Else, it won't.
    :param kwargs: Additional keyword arguments, meant for internal use only.
    :return:
    """
    if not kwargs.get("_color_processor"):
        # Firstly, we add the window to the mapping of windows that we've encountered thus far.
        # This mapping is important because it enables us to obtain the previous theme programmatically
        # at all times, a feature required by Reskinner.
        if window not in list(WINDOW_THEME_MAP.keys()):
            current_theme: str = theme_function()
            WINDOW_THEME_MAP[window] = (current_theme, lf_table[current_theme])

        # Obtain the old and new theme names and themedicts.
        old_theme, old_theme_dict = WINDOW_THEME_MAP[window]
        new_theme_dict = lf_table[new_theme].copy()
        WINDOW_THEME_MAP[window] = (new_theme, new_theme_dict)
        if set_future:
            theme_function(new_theme)

        # Declare a styler object.
        styler = Style()

        # ColorProcessor
        cp: ColorProcessor = ColorProcessor(old_theme_dict, new_theme_dict, styler)
    else:
        cp: ColorProcessor = kwargs.get("_color_processor")
        old_theme = kwargs.get("_old_theme")
        new_theme = kwargs.get("_new_theme")
        styler = cp.styler
        old_theme_dict = cp.old_theme_dict
        new_theme_dict = cp.new_theme_dict

    # Before going any further, we have enough info to disregard redundant calls, so we do so...
    if (new_theme == old_theme) and (new_theme_dict == old_theme_dict):
        return

    # Window level changes
    if reskin_background:
        cp.window(window, {"background": "BACKGROUND"})

    titlebar_row_frame = "Not Set"

    # Handle element filtering
    whitelist = (
        filter(element_filter, window.element_list())
        if element_filter is not None
        else window.element_list()
    )
    # Per-element changes happen henceforth
    for element in whitelist:
        element: Element
        el = _lower_class_name(element)
        # print(el)

        # Generic tweaks
        if (
            getattr(element, "ParentRowFrame", False)
            and element.metadata != TITLEBAR_METADATA_MARKER
        ):
            cp.parent_row_frame(element.ParentRowFrame, {"background": "BACKGROUND"})

        if "background" in element.widget.keys() and element.widget.cget("background"):
            cp.element(element, {"background": "BACKGROUND"})

        # Right Click Menus (thanks for pointing this out @dwelden!)
        if element.TKRightClickMenu:
            cp.recurse_menu(element.TKRightClickMenu)

        # TTK Scrollbars
        if getattr(element, "vsb_style_name", False):
            cp.scrollbar(element.vsb_style_name, "Vertical.TScrollbar")
        if getattr(element, "hsb_style_name", False):
            cp.scrollbar(element.hsb_style_name, "Horizontal.TScrollbar")
        if getattr(
            element, "ttk_style_name", False
        ) and element.ttk_style_name.endswith("TScrollbar"):
            if getattr(element, "Scrollable", False):
                digit, rest = (
                    getattr(element, "ttk_style_name")
                    .replace("Horizontal", "Vertical")
                    .split("_", 1)
                )
                digit = str(int(digit) - 1)
                vertical_style = f"{digit}_{rest}"
                cp.scrollbar(vertical_style, "TScrollbar")
            cp.scrollbar(element.ttk_style_name, "TScrollbar")

        # ACTUAL ELEMENT CUSTOMIZATIONS
        # Custom Titlebar
        if element.metadata == TITLEBAR_METADATA_MARKER:
            cp.element(element, {"background": ("BUTTON", 1)})
            if element.ParentRowFrame:
                cp.parent_row_frame(
                    element.ParentRowFrame, {"background": ("BUTTON", 1)}
                )
            titlebar_row_frame = str(element.ParentRowFrame)
            continue

        # Titlebar elements
        if str(element.widget).startswith(titlebar_row_frame + "."):
            cp.parent_row_frame(element.ParentRowFrame, {"background": ("BUTTON", 1)})
            cp.element(element, {"background": ("BUTTON", 1)})
            if "foreground" in element.widget.keys():
                cp.element(element, {"foreground": ("BUTTON", 0)})
            continue

        # REGULAR ELEMENT CUSTOMIZATIONS
        elif el == "button":  # Button
            if issubclass(element.widget.__class__, TTKWidget):  # For Ttk Buttons.
                style = element.widget.cget("style")
                cp.style(
                    style,
                    {
                        "background": ("BUTTON", 1),
                        "foreground": ("BUTTON", 0),
                    },
                    "TButton",
                )
                cp.map(
                    style,
                    {
                        "background": {
                            "pressed": ("BUTTON", 0),
                            "active": ("BUTTON", 0),
                        },
                        "foreground": {
                            "pressed": ("BUTTON", 1),
                            "active": ("BUTTON", 1),
                        },
                    },
                    "TButton",
                )
                continue
            else:  # For regular buttons.
                cp.element(
                    element,
                    {
                        "background": ("BUTTON", 1),
                        "foreground": ("BUTTON", 0),
                        "activebackground": ("BUTTON", 0),
                        "activeforeground": ("BUTTON", 1),
                    },
                )

        elif el == "buttonmenu":  # ButtonMenu
            cp.element(
                element,
                {
                    "background": ("BUTTON", 1),
                    "foreground": ("BUTTON", 0),
                },
            )
            if getattr(element, "TKMenu", False):
                cp.recurse_menu(element.TKMenu)
            continue

        elif el == "canvas":
            cp.element(element, {"highlightbackground": "BACKGROUND"})

        elif el == "column" and getattr(
            element, "TKColFrame", False
        ):  # Scrollable Column
            element: Column
            if hasattr(
                element.TKColFrame, "canvas"
            ):  # This means the column is scrollable.
                cp.scrollable_column(element)
            continue

        elif el == "combo":  # Combo
            element: Combo
            cp.combo(element)
            continue

        elif el == "frame":  # Frame
            cp.element(element, {"foreground": "TEXT"})
            continue

        elif el == "listbox":  # Listbox
            cp.element(
                element,
                {
                    "foreground": "TEXT_INPUT",
                    "background": "INPUT",
                    "selectforeground": "INPUT",
                    "selectbackground": "TEXT_INPUT",
                },
            )
            continue

        elif el == "menu":  # Menu
            cp.recurse_menu(element.widget)
            continue

        elif el == "progressbar":  # ProgressBar
            element: ProgressBar
            cp.progressbar(element)
            continue

        elif el == "optionmenu":  # OptionMenu
            element: OptionMenu
            cp.optionmenu_menu(
                element,
                {
                    "foreground": "TEXT_INPUT",
                    "background": "INPUT",
                },
            )
            if ALTER_MENU_ACTIVE_COLORS:
                cp.optionmenu_menu(
                    element,
                    {"activeforeground": "INPUT", "activebackground": "TEXT_INPUT"},
                )
            cp.element(element, {"foreground": "TEXT_INPUT", "background": "INPUT"})
            continue

        elif el == "sizegrip":  # Sizegrip
            sizegrip_style = element.widget.cget("style")
            cp.style(sizegrip_style, {"background": "BACKGROUND"}, "TSizegrip")
            continue

        elif el == "slider":  # Slider
            cp.element(element, {"foreground": "TEXT", "troughcolor": "SCROLL"})
            continue

        elif el in "spin":  # Spin
            cp.element(
                element,
                {
                    "background": "INPUT",
                    "foreground": "TEXT_INPUT",
                    "buttonbackground": "INPUT",
                },
            )
            continue

        elif el == "tabgroup":  # TabGroup
            style_name = element.widget.cget("style")
            cp.style(style_name, {"background": "BACKGROUND"}, "TNotebook")
            cp.style(
                f"{style_name}.Tab",
                {"background": "INPUT", "foreground": "TEXT_INPUT"},
                "TNotebook.Tab",
            )
            cp.map(
                f"{style_name}.Tab",
                {
                    "foreground": {"pressed": ("BUTTON", 1), "selected": "TEXT"},
                    "background": {"pressed": ("BUTTON", 0), "selected": "BACKGROUND"},
                },
                f"{style_name}.Tab",
                False,
            )
            continue

        elif el in ("checkbox", "radio"):  # Checkbox, Radio
            element: Union[Checkbox, Radio]
            cp.checkbox_or_radio(element)
            continue

        elif el in (
            "horizontalseparator",
            "verticalseparator",
        ):  # HorizontalSeparator, VerticalSeparator
            style_name = element.widget.cget("style")
            cp.style(style_name, {"background": "BACKGROUND"}, "TSeparator")
            continue

        elif el in ("input", "multiline"):  # Input, Multiline
            cp.element(
                element,
                {
                    "foreground": "TEXT_INPUT",
                    "background": "INPUT",
                    "selectforeground": "INPUT",
                    "selectbackground": "TEXT_INPUT",
                    "insertbackground": "TEXT_INPUT",
                },
            )
            continue

        elif el in ("statusbar", "text"):  # StatusBar, Text
            cp.element(
                element,
                {
                    "background": "BACKGROUND",
                    "foreground": "TEXT",
                },
            )
            continue

        elif el in ("table", "tree"):  # Table, Tree
            element: Union[Table, Tree]
            cp.table_or_tree(element)
            continue
    window.refresh()


def animated_reskin(
    window: Window,
    new_theme: str,
    theme_function: Callable,
    lf_table: dict,
    set_future: bool = True,
    element_filter: Optional[Callable[[Element], bool]] = None,
    reskin_background: bool = True,
    duration_in_milliseconds: float = DEFAULT_ANIMATED_RESKIN_DURATION,
    interpolation_mode: Union[
        RGB_INTERPOLATION, HUE_INTERPOLATION, HSL_INTERPOLATION
    ] = RGB_INTERPOLATION,
):
    delta = timedelta(milliseconds=duration_in_milliseconds)
    start_time = datetime.now()
    end_time = start_time + delta
    # Firstly, we add the window to the mapping of windows that we've encountered thus far.
    # This mapping is important because it enables us to obtain the previous theme programmatically
    # at all times, a feature required by Reskinner.
    if window not in list(WINDOW_THEME_MAP.keys()):
        current_theme: str = theme_function()
        WINDOW_THEME_MAP[window] = (current_theme, lf_table[current_theme])

    # Obtain the old and new theme names and themedicts.
    old_theme, old_theme_dict = WINDOW_THEME_MAP[window]
    new_theme_dict = lf_table[new_theme].copy()
    WINDOW_THEME_MAP[window] = (new_theme, new_theme_dict)
    if set_future:
        theme_function(new_theme)

    # Declare a styler object.
    styler = Style()

    # ColorProcessor
    cp: ColorProcessor = ColorProcessor(
        old_theme_dict, new_theme_dict, styler, 0, interpolation_mode
    )
    while datetime.now() <= end_time:
        cp.progress = round((datetime.now() - start_time) / delta, 4)
        try:
            reskin(
                window,
                new_theme,
                theme_function,
                lf_table,
                set_future,
                element_filter,
                reskin_background,
                _color_processor=cp,
                _old_theme=old_theme,
                _new_theme=new_theme,
            )
        except TclError:  # Closed window.
            return
    cp.progress = 1
    reskin(
        window,
        new_theme,
        theme_function,
        lf_table,
        set_future,
        element_filter,
        reskin_background,
        _color_processor=cp,
        _old_theme=old_theme,
        _new_theme=new_theme,
    )


def toggle_transparency(window: Window) -> None:
    """
    Use this function to toggle background transparency on or off. Works with reskinned and non-reskinned windows.

    First available from v2.0.34.

    :param window: The window to work on.
    :return: None
    """
    window_bg = window.TKroot.cget("background")
    transparent_color = window.TKroot.attributes("-transparentcolor")
    window.set_transparent_color(window_bg if transparent_color == "" else "")


# MAIN FUNCTION
def main():
    """
    Main Function.

    Gets called when the module is run instead of imported.

    First available from v1.0.0.
    """
    # % START DEMO % #
    # from psg_reskinner import animated_reskin, reskin, __version__
    from random import choice as rc

    from PySimpleGUI import (
        LOOK_AND_FEEL_TABLE,
        Button,
        Push,
        Text,
        Titlebar,
        Window,
        theme,
        theme_list,
    )

    right_click_menu = [
        "",
        [["Hi", ["Next Level", ["Deeper Level", ["a", "b", "c"]], "Hoho"]], "There"],
    ]

    window_layout = [
        [Titlebar("Reskinner Demo")],
        [Text("Hello!", font=("Helvetica", 20))],
        [Text("You are currently running the Reskinner demo.")],
        [Text("The theme of this window changes every 2 seconds.")],
        [Text("Changing to:")],
        [
            Button(
                "DarkBlue3",
                k="current_theme",
                font=("Helvetica", 16),
                right_click_menu=right_click_menu,
            )
        ],
        [Text(f"Reskinner v{__version__}", font=("Helvetica", 8), pad=(0, 0)), Push()],
    ]

    window = Window(
        "Reskinner Demo",
        window_layout,
        element_justification="center",
        keep_on_top=True,
    )

    def _reskin_job():
        themes = theme_list()
        themes.remove(theme())
        new = rc(themes)
        window["current_theme"].update(new)
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

        if e in (None, "Exit"):
            window.Close()
            break

        if not started:
            _reskin_job()
            started = True

    # % END DEMO % #
    return
