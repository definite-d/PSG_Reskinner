# Tester Script
# Basically the All Elements Demo program that comes with standard PySimpleGUI, but modified a bit for our purposes.

import PySimpleGUI as sg

# rs = import_by_file("psg_reskinner", "..")
import psg_reskinner as rs

use_divider: bool = True


def all_elements_demo():
    sg.theme("Topanga")
    use_custom_titlebar = True if sg.running_trinket() else False

    NAME_SIZE = 23

    def name(name):
        dots = NAME_SIZE - len(name) - 2
        return sg.Text(
            name + " " + "•" * dots,
            size=(NAME_SIZE, 1),
            justification="r",
            pad=(0, 0),
            font="Courier 10",
        )

    # NOTE that we're using our own LOCAL Menu element
    if use_custom_titlebar:
        Menu = sg.MenubarCustom
    else:
        Menu = sg.Menu
    # Menu = sg.MenubarCustom

    treedata = sg.TreeData()

    treedata.Insert(
        "",
        "_A_",
        "Tree Item 1",
        [1234],
    )
    treedata.Insert("", "_B_", "B", [])
    treedata.Insert(
        "_A_",
        "_A1_",
        "Sub Item 1",
        ["can", "be", "anything"],
    )

    layout_l = [
        [name("Text"), sg.Text("Text")],
        [name("Input"), sg.Input(s=15)],
        [name("Multiline"), sg.Multiline(s=(15, 2))],
        # [name('Output'), sg.Output(s=(15, 2))],
        [
            name("Combo"),
            sg.Combo(
                sg.theme_list(),
                default_value=sg.theme(),
                s=(15, 22),
                enable_events=True,
                readonly=True,
                k="-COMBO-",
            ),
        ],
        [
            name("OptionMenu"),
            sg.OptionMenu(
                [
                    "OptionMenu",
                ],
                k="optionmenu",
                s=(15, 2),
            ),
        ],
        [name("Checkbox"), sg.Checkbox("Checkbox")],
        [name("Radio"), sg.Radio("Radio", 1)],
        [
            name("Spin"),
            sg.Spin(
                [
                    "Spin",
                ],
                s=(15, 2),
            ),
        ],
        [name("Button"), sg.Button("Button")],
        [
            name("ButtonMenu"),
            sg.ButtonMenu("ButtonMenu", sg.MENU_RIGHT_CLICK_EDITME_EXIT),
        ],
        [name("Slider"), sg.Slider((0, 10), orientation="h", s=(10, 15), k="slider")],
        [
            name("Listbox"),
            sg.Listbox(["Listbox", "Listbox 2"], no_scrollbar=True, s=(15, 2)),
        ],
        [name("Image"), sg.Image(sg.EMOJI_BASE64_HAPPY_THUMBS_UP)],
        [name("Graph"), sg.Graph((125, 50), (0, 0), (125, 50), k="-GRAPH-")],
    ]

    layout_r = [
        [
            name("Canvas"),
            sg.Canvas(background_color=sg.theme_button_color()[1], size=(125, 40)),
        ],
        [
            name("ProgressBar"),
            sg.ProgressBar(100, orientation="h", s=(10, 20), k="-PBAR-"),
        ],
        [
            name("Table"),
            sg.Table([[1, 2, 3]], ["Col 1", "Col 2", "Col 3"], num_rows=2),
        ],
        [
            name("Tree"),
            sg.Tree(
                treedata,
                [
                    "Heading",
                ],
                num_rows=3,
            ),
        ],
        [name("Horizontal Separator"), sg.HSep()],
        [name("Vertical Separator"), sg.VSep()],
        [name("Frame"), sg.Frame("Frame", [[sg.T(s=15)]])],
        [name("Column"), sg.Column([[sg.T(s=15)]])],
        [
            name("Tab, TabGroup"),
            sg.TabGroup(
                [[sg.Tab("Tab1", [[sg.T(s=(15, 2))]]), sg.Tab("Tab2", [[]])]],
                right_click_menu=[[""], ["asdfe", "adsfasdfadfs", ";klhjlkjh"]],
            ),
        ],
        [
            name("Pane"),
            sg.Pane([sg.Col([[sg.T("Pane 1")]]), sg.Col([[sg.T("Pane 2")]])]),
        ],
        [name("Push"), sg.Push(), sg.T("Pushed over")],
        [name("VPush"), sg.VPush()],
        # [name('Sizer Custom'), sg.Canvas(size=(10, 10))],
        # [name("Sizer"), sg.Sizer(600, 600)],
        [
            name("Sizer Custom"),
            sg.Column(
                [[]],
                pad=((100, 0), (100, 0)),
                size=(0, 0),
                k="sizer",
                background_color="#d0ff33",
            ),
        ],
        [name("StatusBar"), sg.StatusBar("StatusBar")],
        [name("Sizegrip"), sg.Sizegrip()],
    ]

    # Note - LOCAL Menu element is used (see about for how that's defined)
    menudef = [
        ["File", ["Exit"]],
        ["Edit", ["Edit Me", "---" if use_divider else "adsfasfd", "asdf"]],
    ]
    layout = [
        [Menu(menudef, k="-CUST MENUBAR-", p=0)],
        [
            sg.T(
                "PySimpleGUI Elements - Use Combo to Change Themes",
                font="_ 14",
                justification="c",
                expand_x=True,
            )
        ],
        [
            sg.Checkbox(
                "Use Custom Titlebar & Menubar",
                use_custom_titlebar,
                enable_events=True,
                k="-USE CUSTOM TITLEBAR-",
                p=0,
                tooltip="checkcheckcheck",
            )
        ],
        [sg.Col(layout_l, p=0, scrollable=True), sg.Col(layout_r, p=0)],
    ]

    window = sg.Window(
        "The PySimpleGUI Element List",
        [[sg.Col(layout, scrollable=True, key="allfather")]],
        finalize=True,
        right_click_menu=sg.MENU_RIGHT_CLICK_EDITME_VER_EXIT,
        # keep_on_top=True,
        use_custom_titlebar=use_custom_titlebar,
        resizable=True,
    ).finalize()

    # window["sizer"].set_tooltip(str(window["sizer"].widget))

    window["-PBAR-"].update(30)  # Show 30% complete on ProgressBar
    window["-GRAPH-"].draw_image(
        data=sg.EMOJI_BASE64_HAPPY_JOY, location=(0, 50)
    )  # Draw something in the Graph Element

    # print('window', window.TKroot.cget('bg'))
    # for element in sorted(set(type(el).__name__ for el in window.element_list())):
    #     print(element)
    print(window["optionmenu"].widget["menu"].cget("background"))
    while True:
        event, values = window.Read()

        if event == sg.WIN_CLOSED or event == "Exit":
            break

        if event == "-COMBO-":
            # rs.reskin(
            rs.animated_reskin(
                window,
                values["-COMBO-"],
                sg.theme,
                sg.LOOK_AND_FEEL_TABLE,
            )
        if event == "-USE CUSTOM TITLEBAR-":
            use_custom_titlebar = values["-USE CUSTOM TITLEBAR-"]
            sg.set_options(use_custom_titlebar=use_custom_titlebar)
            # window.close()
        if event == "Edit Me":
            sg.execute_editor(__file__)
        elif event == "Version":
            sg.popup_scrolled(
                __file__, sg.get_versions(), keep_on_top=True, non_blocking=True
            )
    window.close()


if __name__ == "__main__":
    all_elements_demo()
