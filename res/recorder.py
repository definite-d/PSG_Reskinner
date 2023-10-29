"""
This script is used to run the demo and automatically record a GIF of the demo window,
then save the GIF. It relies on ShareX, and the shortcut for GIF recording being set to
Ctrl+Shift+Alt+S.
Have ShareX open and the shortcout key set for this script to work well.
"""
import re
from inspect import getsource
from typing import Callable

from import_util import import_by_file

psg_reskinner = import_by_file("psg_reskinner", "..")
reskin = psg_reskinner.reskin
animated_reskin = psg_reskinner.animated_reskin
__version__ = psg_reskinner.version.__version__

SHORTCUT: str = "Ctrl+Shift+Alt+S"
_main: Callable = psg_reskinner.psg_reskinner.main
lines: str = getsource(_main).replace("\n", "\\n")
window_line: str = re.search(r"window = Window\([^)]*\)", lines).group()
modified_code: str = f"""
    {window_line}
    from keyboard import send
    default_theme = theme()
    themes = [default_theme, 'Black', 'DarkTanBlue', 'GrayGrayGray', 'DarkRed1', 'Reds', 'DarkGrey12', 
              'DarkBlue12', 'Topanga', 'SystemDefaultForReal', 'NeonGreen1']

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
    send(SHORTCUT)
    window.read(20)
    while True:
        e, v = window.read(timeout=2000)
        if len(themes) == 0:
            send(SHORTCUT)
            break

        if (e in (None, 'Exit')):
            window.close()
            break

        if not started:
            _reskin_job()
            started = True

    # % END DEMO % #
    # return
"""
newlines = re.sub(r"\\n    window = Window\([^)]*\).*", modified_code, lines).replace(
    "\\n", "\n"
)
exec(newlines)

main()
