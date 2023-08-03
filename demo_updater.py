import re
from inspect import getsourcelines
from psg_reskinner.__main__ import main

print('Demo Updater active.')

# First we get the lines of code that make up the demo.
print('\rObtaining demo code from main function...', end='')
DEMO_START = '    # % START DEMO % #\n'
DEMO_END = '    # % END DEMO % #\n'
demo_lines = getsourcelines(main)
demo_lines = demo_lines[0][
                demo_lines[0].index(DEMO_START) + 1: demo_lines[0].index(DEMO_END)
             ]
# Remove the indent from each line and the final newline.
demo_lines = ''.join([_line[4:] for _line in demo_lines])[:-1]

# Then the hydration occurs.
with open('./README_DRY.md', 'r') as readme:
    print('\rReading dry README file...', end='')
    data = readme.read()
    pattern = re.compile(r'# Demo code goes here. Run the demo_updater.py script to hydrate it.')
    print('\rConstructing new README...', end='')
    new_data = re.sub(pattern, demo_lines, data)
    with open('./README.md', 'w') as out:
        # And done.
        print('\rWriting new README to file...', end='')
        out.write(new_data)
        print('\rREADME updated successfully with demo code from main().')
