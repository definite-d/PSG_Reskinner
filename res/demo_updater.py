import re
from inspect import getsourcelines

from import_util import import_by_file

main = (import_by_file('psg_reskinner', '..')).__main__.main

DRY_README_PATH = './README_DRY.md'
README_PATH = '../README.md'
START_DEMO = '# % START DEMO % #'
END_DEMO = '# % END DEMO % #'

print('Updating Demo Code in main README.', end='')

print('\rObtaining demo code from main function...', end='')

# Change the newlines on each line to literal slashes and n's, eliminate indents and join those lines
# back together.
source = ''.join(
    [''.join(str(line).replace('\n', r'\n').split('    ', maxsplit=1)) for line in getsourcelines(main)[0]]
)
demo_code_pattern = re.compile(fr'{START_DEMO}.*{END_DEMO}')

# We're doing some crazy RegEx magic here, but basically we find the start and end points of the demo,
# get the string from that start to end, remove the start and end indicators (and their newlines,
# which now take up 2 characters because we converted them to r initially) and change the newlines
# back to their original form.
demo_lines = re.search(
    demo_code_pattern,
    source
).group(0)[len(START_DEMO)+4:-(len(END_DEMO)+2)].replace(r'\n', '\n')

# Then the hydration occurs.
with open(DRY_README_PATH, 'r') as readme:
    print('\rReading dry README file...', end='')
    data = readme.read()
    pattern = re.compile(r'# Demo code goes here. Run the demo_updater.py script to hydrate it.')
    print('\rConstructing new README...', end='')
    new_data = re.sub(pattern, demo_lines, data)
with open(README_PATH, 'w') as out:
    # And done.
    print('\rWriting new README to file...', end='')
    out.write(new_data)
    print('\rREADME updated successfully with demo code from main().')
