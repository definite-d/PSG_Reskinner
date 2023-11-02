"""
This script is used to run the demo and automatically record a GIF of the demo window,
then save the GIF. It relies on ShareX, and the shortcut for GIF recording being set to
Ctrl+Shift+Alt+R.
Have ShareX open and the shortcut key set for this script to work well.
"""
import re
from inspect import getsource

from psg_reskinner.psg_reskinner import main

exec(
    """
from pyautogui import press
from typing import Callable
from psg_reskinner import reskin, animated_reskin, __version__
    """
)

SHORTCUT: str = "Ctrl+Shift+Alt+R"
from keyboard import press

press(SHORTCUT)
lines: str = getsource(main).replace("\n", "\\n")
window_line: str = re.search(r"window = Window\([^)]*\)", lines).group()
modified_code: str = f"""
    {window_line}
    default_theme = theme()
    themes = [default_theme, 'Black', 'GrayGrayGray', 'DarkRed1', 'Reds', 'DarkGrey12', 
              'DarkBlue12', 'Topanga', 'SystemDefault', 'NeonGreen1']

    def _reskin_job():
        new = themes.pop()
        window['current_theme'].update(new)
        animated_reskin(
            window=window,
            new_theme=new,
            theme_function=theme,
            lf_table=LOOK_AND_FEEL_TABLE,
        )
        window.TKroot.after(2000, _reskin_job)

    started = False
    window.finalize()
    window.read(10)
    press(SHORTCUT)
    window.read(20)
    while True:
        e, v = window.read(timeout=2000)
        if len(themes) == 0:
            press(SHORTCUT)
            break

        if (e in (None, 'Exit')):
            window.close()
            break

        if not started:
            _reskin_job()
            started = True

    # % END DEMO % #
    # return
""".replace(
    "\\n", "\n"
)
print(modified_code)
newlines = re.sub(r"\\n    window = Window\([^)]*\).*", modified_code, lines).replace(
    "\\n", "\n"
)
exec(newlines)

main()
