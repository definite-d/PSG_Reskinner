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
