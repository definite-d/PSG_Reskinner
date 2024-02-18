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

from functools import cache
from tkinter import Frame as TKFrame
from tkinter import Menu as TKMenu
from tkinter import Widget
from tkinter.ttk import Style
from typing import Any, Callable, Dict, Tuple, Union

from PySimpleGUI import (
    COLOR_SYSTEM_DEFAULT,
    DEFAULT_PROGRESS_BAR_COMPUTE,
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
    rgb,
)
from PySimpleGUI.PySimpleGUI import _hex_to_hsl, _hsl_to_rgb  # noqa
from colour import Color

from .constants import (
    HSL_INTERPOLATION,
    HUE_INTERPOLATION,
    RGB_INTERPOLATION,
    SCROLLBAR_ARROW_COLOR,
    SCROLLBAR_BACKGROUND_COLOR,
    SCROLLBAR_FRAME_COLOR,
    SCROLLBAR_TROUGH_COLOR,
)
from .default import _default_elements, _default_window
from .utilities import _lower_class_name, clamp


def _pbcompute(theme_dict: Dict, create_new_copy: bool = True):
    if theme_dict["PROGRESS"] == DEFAULT_PROGRESS_BAR_COMPUTE:
        theme_dict = theme_dict.copy() if create_new_copy else theme_dict
        if (
            theme_dict["BUTTON"][1] != theme_dict["INPUT"]
            and theme_dict["BUTTON"][1] != theme_dict["BACKGROUND"]
        ):
            theme_dict["PROGRESS"] = (theme_dict["BUTTON"][1], theme_dict["INPUT"])
        else:
            theme_dict["PROGRESS"] = (theme_dict["TEXT_INPUT"], theme_dict["INPUT"])
    return theme_dict


def _cgetde(element_name: str, attribute: str):
    """
    Internal use only.

    Shortcut function that calls the cget function of a default element.

    First available from v3.0.0.
    :param element_name: The name of the element.
    :param attribute: The attribute to pass to the cget function.
    :return: The result of the cget function.
    """
    return _default_elements[element_name].widget[attribute]


def _cgetdw(attribute: str):
    """
    Internal use only.

    Shortcut function that calls the cget function of the default window.

    First available from v3.0.0.
    :param attribute: The attribute to pass to the cget function.
    :return: The result of the cget function.
    """
    return _default_window.TKroot[attribute]


def _is_valid_color(color: str) -> bool:
    """
    Internal use only.

    Checks if a color is valid or not

    First available from v3.0.0.
    :param color: A color string to be checked.
    :return: True or False.
    """
    if not color:
        return False
    try:
        Color(color).get_hex_l()
    except ValueError:
        return False
    else:
        return True


def _normalize_tk_color(tk_color) -> str:
    """
    Internal use only.

    Converts TK system colors to regular hex colors.

    First available from v3.0.0.
    :param tk_color: The TK color to be converted.
    :return: A hex color string.
    """
    result = Color()
    result.set_rgb(tuple(x / 65535 for x in _default_window.TKroot.winfo_rgb(tk_color)))
    return result.get_hex_l()


@cache
def _ds(
    value: Union[str, type(COLOR_SYSTEM_DEFAULT)],
    default_function: Callable,
):
    """
    Internal use only.

    Stands for "default-safe".

    If the value is a safe color, we return that. Otherwise, we get a reasonable default with the fallbacks given.

    First available from v2.4.0.

    :param default_function: A function that returns the value that should be used as default.
    :param value: The value to check for safety.
    :return: A TK-safe color, no matter what the input value is.
    """
    if _is_valid_color(value):
        return value
    return _normalize_tk_color(default_function())


def checkbox_radio_selectcolor(background_color, text_color) -> str:
    # PySimpleGUI's color conversion functions give different results than those of the colour module, so I can't
    # use the color module's functionality for everything here.
    if not all([_is_valid_color(background_color), _is_valid_color(text_color)]):
        return _cgetde("checkbox", "selectcolor") or "black"
    background_color: str = Color(background_color).get_hex_l()
    text_color: str = Color(text_color).get_hex_l()
    background_hsl: Tuple[float, float, float] = _hex_to_hsl(background_color)
    text_hsl: Tuple[float, float, float] = _hex_to_hsl(text_color)
    l_delta: float = (
        abs(text_hsl[2] - background_hsl[2])
        / 10
        * (1 if text_hsl[2] < background_hsl[2] else -1)
    )
    rgb_ = _hsl_to_rgb(
        background_hsl[0], background_hsl[1], background_hsl[2] + l_delta
    )
    result: str = rgb(*rgb_)
    return result


class ColorProcessor:
    def __init__(
        self,
        old_theme_dict: Dict[str, Any],
        new_theme_dict: Dict[str, Any],
        styler: Style,
        progress: float = 1,
        mode: Union[
            RGB_INTERPOLATION, HUE_INTERPOLATION, HSL_INTERPOLATION
        ] = RGB_INTERPOLATION,
    ):
        self.mode = mode
        self.new_theme_dict = _pbcompute(new_theme_dict)
        self.old_theme_dict = _pbcompute(old_theme_dict)
        self.progress = progress
        self.styler = styler

    def _transition(
        self,
        old_color: Color,
        new_color: Color,
    ) -> str:
        """
        Internal use only.

        Performs an interpolation calculation between two colors (old_color and new_color) and returns a Color object as
        the result. Inspired by https://www.alanzucconi.com/2016/01/06/colour-interpolation/.

        - RGB interpolation is simple lerping through RGB color space.
        - Hue interpolation is lerping through HSL color space but moving only forward on the hue scale until it
            reaches the new color.
        - HSV interpolation also lerps across HSL color space, but it takes the shortest route to get to the new color.

        Note: "lerp" means "linear-interpolation", in case you didn't know.

        Each interpolation mode has a different visual effect which may look better than the others in certain
        scenarios.

        First available from v3.0.0.
        :return: A transitioned color string.
        """
        result = Color()
        if self.progress == 1:
            return new_color.get_hex_l()
        elif self.progress == 0:
            return old_color.get_hex_l()

        if self.mode == RGB_INTERPOLATION:
            result.set_red(
                clamp(
                    old_color.get_red()
                    + ((new_color.get_red() - old_color.get_red()) * self.progress)
                )
            )
            result.set_green(
                clamp(
                    old_color.get_green()
                    + ((new_color.get_green() - old_color.get_green()) * self.progress)
                )
            )
            result.set_blue(
                clamp(
                    old_color.get_blue()
                    + ((new_color.get_blue() - old_color.get_blue()) * self.progress)
                )
            )
        elif self.mode == HUE_INTERPOLATION:
            result.set_hue(
                clamp(
                    old_color.get_hue()
                    + ((new_color.get_hue() - old_color.get_hue()) * self.progress)
                )
            )
            result.set_saturation(
                clamp(
                    old_color.get_saturation()
                    + (
                        (new_color.get_saturation() - old_color.get_saturation())
                        * self.progress
                    )
                )
            )
            result.set_luminance(
                clamp(
                    old_color.get_luminance()
                    + (
                        (new_color.get_luminance() - old_color.get_luminance())
                        * self.progress
                    )
                )
            )
        elif self.mode == HSL_INTERPOLATION:
            if old_color.get_hue() > new_color.get_hue():
                old_color, new_color = (new_color, old_color)
                self.progress = 1 - self.progress
            diff = new_color.get_hue() - old_color.get_hue()
            if diff > 0.5:
                hue = (
                    (old_color.get_hue() + 1)
                    + self.progress * (new_color.get_hue() - (old_color.get_hue() + 1))
                ) % 1
            else:
                hue = old_color.get_hue() + self.progress * diff
            result.set_hue(clamp(hue))
            result.set_saturation(
                clamp(
                    old_color.get_saturation()
                    + (
                        (new_color.get_saturation() - old_color.get_saturation())
                        * self.progress
                    )
                )
            )
            result.set_luminance(
                clamp(
                    old_color.get_luminance()
                    + (
                        (new_color.get_luminance() - old_color.get_luminance())
                        * self.progress
                    )
                )
            )
        return result.get_hex_l()

    def config(
        self,
        configs: Dict[str, Union[Color, str]],
        config_function: Callable,
        default_function: Callable,
    ) -> None:
        """
        Internal use only.

        Configures anything (elements, widgets, styles etc.) safely by calling a config function and supplying processed
        colors.

        First available from v3.0.0.
        :param config_function: A callable for the configuration.
        :param configs: The configuration arguments, in the format of attribute: theme_dict_key.
        :param default_function: A callable for obtaining the default values. Must accept a string for the attribute
            being obtained.
        :return: None
        """
        _configs = {
            attribute: self._processed(
                theme_dict_key,
                cache(lambda: default_function(attribute)),
            )
            for attribute, theme_dict_key in configs.items()
        }
        config_function(**_configs)

    def element(
        self,
        element: Element,
        configs: Dict[str, Union[str, Tuple[str, int]]],
    ):
        self.config(
            configs,
            element.widget.configure,
            lambda attribute: _cgetde(
                _lower_class_name(element),
                attribute,
            ),
        )

    def style(
        self,
        style: str,
        configs: Dict[str, Union[str, Tuple[str, int]]],
        default_style: str,
        fallback: str = "black",
    ):
        # if self.styler.configure(style) is None:
        #     raise ReskinnerException(f"`{style}` doesn't exist.")
        self.config(
            configs,
            lambda **kwargs: self.styler.configure(style, **kwargs),
            lambda attribute: self.styler.lookup(
                default_style, attribute, default=fallback
            ),
        )

    def map(
        self,
        style: str,
        configs: Dict[str, Dict[str, Union[Tuple[str, int], str]]],
        default_style: str,
        pass_state: bool = False,
        fallback: str = "black",
    ) -> None:
        # if self.styler.configure(style) is None:
        #     raise ReskinnerException(f"`{style}` doesn't exist.")
        values = {
            config_k: [
                (
                    k,
                    self._processed(
                        v,
                        lambda: self.styler.lookup(
                            default_style,
                            config_k,
                            [k] if pass_state else None,
                            fallback,
                        ),
                    ),
                )
                for k, v in config_v.items()
            ]
            for config_k, config_v in configs.items()
        }
        self.styler.map(style, **values)

    def window(
        self,
        window: Window,
        configs: Dict[str, Union[str, Tuple[str, int]]],
    ):
        self.config(configs, window.TKroot.configure, _cgetdw)

    def parent_row_frame(
        self,
        parent_row_frame: TKFrame,
        configs: Dict[str, Union[str, Tuple[str, int]]],
    ):
        self.config(
            configs,
            parent_row_frame.configure,
            getattr(_default_elements["text"], "ParentRowFrame").cget,
        )

    def menu_entry(
        self,
        menu: TKMenu,
        index: int,
        configs: Dict[str, Union[str, Tuple[str, int]]],
    ):
        configs = dict(
            filter(
                lambda item: item[0] in menu.entryconfigure(index).keys(),
                configs.items(),
            )
        )  # Filter the configs for menu entries that don't accept the full config dict. Fixes issue #11.
        self.config(
            configs,
            lambda **cnf: menu.entryconfigure(index, cnf),
            lambda attribute: _cgetde("menu", attribute),
        )

    def combo_popdown(
        self,
        combo: Combo,
        configs: Dict[str, Union[str, Tuple[str, int]]],
    ):
        def _combo_popdown_default_getter(attribute):
            _default_window.TKroot.tk.call(
                "eval",
                f"set defaultcombo [ttk::combobox::PopdownWindow {_default_elements['combo'].widget}]",
            )
            return _default_window.TKroot.tk.call(
                "eval", f"$defaultcombo.f.l cget -{attribute}"
            )

        combo.widget.tk.call(
            "eval", f"set popdown [ttk::combobox::PopdownWindow {combo.widget}]"
        )

        def _combo_popdown_configurer(**kwargs):
            command = "$popdown.f.l configure"
            for attribute, value in kwargs.items():
                command += f" -{attribute} {value}"
            combo.widget.tk.call("eval", command)

        self.config(configs, _combo_popdown_configurer, _combo_popdown_default_getter)

    def optionmenu_menu(
        self,
        optionmenu: OptionMenu,
        configs: Dict[str, Union[str, Tuple[str, int]]],
    ):
        self.config(
            configs,
            optionmenu.widget["menu"].configure,
            _default_elements["optionmenu"].widget["menu"].cget,
        )

    def scrollbar(
        self,
        style_name: str,
        default_style: str,
    ):
        self.style(
            style_name,
            {
                "troughcolor": SCROLLBAR_TROUGH_COLOR,
                "framecolor": SCROLLBAR_FRAME_COLOR,
                "bordercolor": SCROLLBAR_FRAME_COLOR,
            },
            default_style,
        )
        self.map(
            style_name,
            {
                "background": {
                    "selected": SCROLLBAR_BACKGROUND_COLOR,
                    "active": SCROLLBAR_ARROW_COLOR,
                    "background": SCROLLBAR_BACKGROUND_COLOR,
                    "!focus": SCROLLBAR_BACKGROUND_COLOR,
                },
                "arrowcolor": {
                    "selected": SCROLLBAR_ARROW_COLOR,
                    "active": SCROLLBAR_BACKGROUND_COLOR,
                    "background": SCROLLBAR_BACKGROUND_COLOR,
                    "!focus": SCROLLBAR_ARROW_COLOR,
                },
            },
            default_style,
        )

    def recurse_menu(self, tkmenu: Union[TKMenu, Widget]):
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

        # This fixes issue #8. Thank you, @richnanney for reporting!
        if tkmenu.index("end") is None:
            return

        for index in range(0, tkmenu.index("end") + 1):
            self.menu_entry(
                tkmenu,
                index,
                {
                    "foreground": "TEXT_INPUT",
                    "background": "INPUT",
                    "activeforeground": "INPUT",
                    "activebackground": "TEXT_INPUT",
                },
            )

        for child in tkmenu.children.values():
            if issubclass(type(child), TKMenu):
                self.recurse_menu(child)

    def scrollable_column(self, column: Column):
        self.config(
            {"background": "BACKGROUND"},
            column.TKColFrame.configure,
            _default_elements["column"].TKColFrame.cget,
        )
        self.config(
            {"background": "BACKGROUND"},
            getattr(column.TKColFrame, "canvas").children["!frame"].configure,
            getattr(_default_elements["column"].TKColFrame, "canvas")
            .children["!frame"]
            .cget,
        )

    def combo(self, combo: Combo):
        # Configuring the listbox of the combo.
        def _combo_listbox_default_getter(default_attribute):
            cache(
                lambda: _default_window.TKroot.tk.call(
                    "eval",
                    f"set defaultcombo [ttk::combobox::PopdownWindow {_default_elements['combo'].widget}]",
                )
            )()
            return _default_window.TKroot.tk.call(
                "eval", f"$defaultcombo.f.l cget -{default_attribute}"
            )

        combo.widget.tk.call(
            "eval", f"set popdown [ttk::combobox::PopdownWindow {combo.widget}]"
        )

        def _combo_listbox_configurer(**kwargs):
            for attribute, value in kwargs.items():
                combo.widget.tk.call(
                    "eval", f"$popdown.f.l configure -{attribute} {value}"
                )

        self.config(
            {
                "background": "INPUT",
                "foreground": "TEXT_INPUT",
                "selectforeground": "INPUT",
                "selectbackground": "TEXT_INPUT",
            },
            _combo_listbox_configurer,
            _combo_listbox_default_getter,
        )
        # Configuring the combo itself.
        style_name = combo.widget["style"]
        self.style(
            style_name,
            {
                "selectforeground": "TEXT_INPUT",
                "selectbackground": "INPUT",
                "selectcolor": "TEXT_INPUT",
                "foreground": "TEXT_INPUT",
                "background": ("BUTTON", 1),
                "arrowcolor": ("BUTTON", 0),
            },
            _cgetde("combo", "style"),
        )
        self.map(
            style_name,
            {
                "foreground": {"readonly": "TEXT_INPUT"},
                "fieldbackground": {"readonly": "INPUT"},
            },
            _cgetde("combo", "style"),
            True,
        )

    def checkbox_or_radio(self, element: Union[Checkbox, Radio]):
        element_name = _lower_class_name(element)
        toggle = checkbox_radio_selectcolor(
            self._processed(
                "BACKGROUND",
                lambda: _cgetde(element_name, "selectcolor"),
            ),
            self._processed(
                "TEXT",
                lambda: _cgetde(element_name, "selectcolor"),
            ),
        )
        element.widget.configure(
            {"selectcolor": toggle}
        )  # A rare case where we use the configure method directly.
        self.element(
            element,
            {
                "background": "BACKGROUND",
                "foreground": "TEXT",
                "activebackground": "BACKGROUND",
                # "text": "TEXT",
            },
        )

    def table_or_tree(self, element: Union[Table, Tree]):
        style_name = element.widget["style"]
        element_name = _lower_class_name(element)
        default_style = _cgetde(element_name, "style")
        self.style(
            style_name,
            {
                "foreground": "TEXT",
                "background": "BACKGROUND",
                "fieldbackground": "BACKGROUND",
                "fieldcolor": "TEXT",
            },
            default_style,
            fallback="white",
        )
        self.map(
            style_name,
            {
                "foreground": {
                    "selected": ("BUTTON", 0),
                },
                "background": {
                    "selected": ("BUTTON", 1),
                },
            },
            default_style,
            True,
            fallback="white",
        )
        self.style(
            f"{style_name}.Heading",
            {
                "foreground": "TEXT_INPUT",
                "background": "INPUT",
            },
            f"{default_style}.Heading",
        )

        if element_name == "table":
            self.map(
                f"{style_name}.Heading",
                {
                    "foreground": {"active": "INPUT"},
                    "background": {"active": "TEXT_INPUT"},
                },
                f"{default_style}.Heading",
                True,
            )

    def progressbar(self, element: ProgressBar):
        style_name = element.ttk_style_name
        self.style(
            style_name,
            {"background": ("PROGRESS", 0), "troughcolor": ("PROGRESS", 1)},
            _cgetde("progressbar", "style"),
        )

    def _processed(
        self,
        theme_dict_key: str,
        default_function: Callable[[Any], str],
    ):
        """

        :param theme_dict_key: The key of the target value in the theme_dicts.
        :param default_function:
        :return:
        """
        theme_dict_key, theme_dict_index = (
            theme_dict_key
            if isinstance(theme_dict_key, (list, tuple))
            else (theme_dict_key, None)
        )
        old_color, new_color = (
            (
                self.old_theme_dict[theme_dict_key],
                self.new_theme_dict[theme_dict_key],
            )
            if theme_dict_index is None
            else (
                self.old_theme_dict[theme_dict_key][theme_dict_index],
                self.new_theme_dict[theme_dict_key][theme_dict_index],
            )
        )
        old_color = Color(
            _ds(
                old_color,
                default_function,
            )
        )
        new_color = Color(
            _ds(
                new_color,
                default_function,
            )
        )
        return self._transition(old_color, new_color)

    # def fixedframe_canvas(self, element):
    #     children: Dict[str, Widget] = getattr(element.widget, "children", {})
    #     if children.get("!canvas", False):
    #         print(element.widget.children["!canvas"].configure())
    #         print(element.widget.children["!canvas"].children["!frame"].configure())
    #         self.config(
    #             {"background": "BACKGROUND"},
    #             element.widget.children["!canvas"].configure,
    #             lambda attribute: _cgetde("canvas", attribute),
    #         )
    #         self.config(
    #             {
    #                 "background": "BACKGROUND",
    #                 "highlightcolor": "BACKGROUND",
    #                 "highlightbackground": "BACKGROUND",
    #             },
    #             element.widget.children["!canvas"].children["!frame"].configure,
    #             lambda attribute: _cgetde("canvas", attribute),
    #         )
