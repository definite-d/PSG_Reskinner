import re
from datetime import datetime

print('Updating the copyright year in the DESCRIPTION file...', end='')

pattern = re.compile(r'Copyright \(c\) [0-9]* Afam\-Ifediogor Divine\.')
replacement = fr'Copyright (c) {datetime.now().year} Afam-Ifediogor Divine.'

with open('DESCRIPTION.md', 'r') as desc:
    content = desc.read().replace('\n', r'\n')
    content = re.sub(pattern, replacement, content)
    content = content.replace(r'\n', '\n')

with open('DESCRIPTION.md', 'w') as desc:
    desc.write(content)

print('\rDESCRIPTION file year updated successfully.')
