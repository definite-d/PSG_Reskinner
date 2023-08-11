"""
Build script for psg_reskinner.
"""

from subprocess import run
from datetime import datetime
from bumpver.version import parse_version
from import_util import import_by_file
from os.path import abspath

VERSION = (import_by_file('psg_reskinner', '..')).__version__
print(f'Working with Reskinner v{VERSION}.')

DEFAULT_UPLOAD_DESTINATION = 'legacy'
DEFAULT_OUTPUT_DIR = f'dist/v{parse_version(VERSION).major}/{VERSION}'
WORKING_DIR = abspath('../')

with open('../.env', 'r') as env:
    TOKEN = env.readline()

def build():
    """
    Builds the project.
    """
    print('Building...')
    run(f'python -m build -n --outdir=./{DEFAULT_OUTPUT_DIR}/', cwd=WORKING_DIR)


def commit(message: str = f'New Commit at {datetime.now()}'):
    """
    Commits files to local repository.
    """
    print('Staging commit...')
    run(f'git commit -m "{message}" -a', cwd=WORKING_DIR)


def upload_testpypi(version: str = VERSION):
    """
    Uploads the project to PyPi's test server.
    :param version: The specific version to upload.
    """
    print('Uploading to TestPyPi...')
    run(f'twine upload --username __token__ --password {TOKEN} --repository testpypi {DEFAULT_OUTPUT_DIR}/psg_reskinner-{version}*', cwd=WORKING_DIR)


def upload_legacy(version: str = VERSION):
    """
    Uploads the project to PyPi's legacy servers.
    :param version: The specific version to upload.
    """
    print('Uploading to PyPi...')
    run(f'twine upload --username __token__ --password {TOKEN} --repository-url https://upload.pypi.org/legacy/ {DEFAULT_OUTPUT_DIR}/psg_reskinner-{version}*', cwd=WORKING_DIR)


def bumpver(major: bool = False, minor: bool = False, patch: bool = True):
    """
    Internal use only.

    Bumps the version a notch using the BumpVer tool.
    """
    print('Updating version...')
    if sum([major, minor, patch]) != 1:
        raise Exception('One (and only one) of major, minor or patch must be set!')
    target = 'major' if major else 'minor' if minor else 'patch'
    run(f'bumpver update --{target}', cwd=WORKING_DIR)


def update_demo():
    """
    Internal use only.

    Updates the README with the demo code.
    """
    run('python demo_updater.py')


def update_description_year():
    """
    Internal use only.

    Updates the copyright year of the DESCRIPTION.
    """
    run('python description_year_updater.py')


update_demo()
update_description_year()
commit()
# bumpver()
# build()
# upload_legacy()
