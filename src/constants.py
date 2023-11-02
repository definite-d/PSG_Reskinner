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

from PySimpleGUI import ttk_part_mapping_dict

ALTER_MENU_ACTIVE_COLORS = True
DEFAULT_ANIMATED_RESKIN_DURATION = 450
DISABLED_COLOR = "#A3A3A3"
HSL_INTERPOLATION = "hsv"
HUE_INTERPOLATION = "hue"
NON_GENERIC_ELEMENTS = [
    "button",
    "horizontalseparator",
    "listbox",
    "multiline",
    "progressbar",
    "sizegrip",
    "spin",
    "tabgroup",
    "table",
    "text",
    "tree",
    "verticalseparator",
]
RGB_INTERPOLATION = "rgb"
WINDOW_THEME_MAP = {}
MAPPER = {
    "Background Color": "BACKGROUND",
    "Button Background Color": ("BUTTON", 1),
    "Button Text Color": ("BUTTON", 0),
    "Input Element Background Color": "INPUT",
    "Input Element Text Color": "TEXT_INPUT",
    "Text Color": "TEXT",
    "Slider Color": "SCROLL",
}
SCROLLBAR_TROUGH_COLOR: str = MAPPER[ttk_part_mapping_dict["Trough Color"]]
SCROLLBAR_FRAME_COLOR: str = MAPPER[ttk_part_mapping_dict["Frame Color"]]
SCROLLBAR_BACKGROUND_COLOR: str = MAPPER[ttk_part_mapping_dict["Background Color"]]
SCROLLBAR_ARROW_COLOR: str = MAPPER[ttk_part_mapping_dict["Arrow Button Arrow Color"]]
