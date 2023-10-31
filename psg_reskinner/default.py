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
from PySimpleGUI import (
    MENU_RIGHT_CLICK_EDITME_EXIT,
    Button,
    ButtonMenu,
    Canvas,
    Checkbox,
    Column,
    Combo,
    Frame,
    Graph,
    HorizontalSeparator,
    Image,
    Input,
    Listbox,
    Menu,
    Multiline,
    OptionMenu,
    Pane,
    ProgressBar,
    Radio,
    Sizegrip,
    Slider,
    Spin,
    StatusBar,
    Tab,
    TabGroup,
    Table,
    Text,
    Tree,
    TreeData,
    VerticalSeparator,
    Window,
    theme,
)

_previous_theme = theme()
theme("GrayGrayGray")

_tree_data = TreeData()
_tree_data.Insert(
    "",
    "_A_",
    "Tree Item 1",
    [1234],
)


# DEFAULT ELEMENTS
# The most minimal declarations for all elements. I wish there was an easier (or less hardcoded) way.
_default_elements = {
    "button": Button(),
    "buttonmenu": ButtonMenu("", MENU_RIGHT_CLICK_EDITME_EXIT),
    "canvas": Canvas(),
    "checkbox": Checkbox(""),
    "column": Column([[Text()]], scrollable=True),
    "combo": Combo([""]),
    "frame": Frame("", [[Text()]]),
    "graph": Graph((2, 2), (0, 2), (2, 0)),
    "horizontalseparator": HorizontalSeparator(),  # 'image': sg.Image(),
    "input": Input(),
    "image": Image(),
    "listbox": Listbox([""]),
    "menu": Menu([["File", ["Exit"]], ["Edit", ["Edit Me"]]]),
    "multiline": Multiline(),
    "optionmenu": OptionMenu([""]),
    "pane": Pane([Column([[Text()]]), Column([[Text()]])]),
    "progressbar": ProgressBar(0),
    "radio": Radio("", 0),
    "sizegrip": Sizegrip(),
    "slider": Slider(),
    "spin": Spin([0]),
    "statusbar": StatusBar(""),
    "tabgroup": TabGroup([[Tab("", [[Text()]], key="tab")]]),
    "table": Table([["asdf"]]),
    "text": Text(),
    "tree": Tree(_tree_data, [""], num_rows=1),
    "verticalseparator": VerticalSeparator(),
}
# A completely invisible window, which should at worst show a
# small line at the top-right of the left display if
# viewed on a Raspberry Pi with multiple monitors. Unlikely.
_default_window = Window(
    "",
    [[element] for element in _default_elements.values()],
    size=(1, 1),
    no_titlebar=True,
    alpha_channel=0,
    location=(-1, -1),
).finalize()

_default_elements["tab"] = _default_window["tab"]
theme(_previous_theme)
