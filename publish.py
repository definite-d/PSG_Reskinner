"""
Build script for psg_reskinner.

Usage:

To build and upload to legacy PyPi
> python -m publish.py legacy
"""
from psg_reskinner import __version__ as VERSION
from os import system
from datetime import datetime
from bumpver.version import parse_version
from argparse import ArgumentParser as p


DEFAULT_UPLOAD_DESTINATION = 'legacy'

with open('./.env', 'r') as env:
    TOKEN = env.readline()


def build():
    """
    Builds the project.
    """
    system(f'python -m build -n --outdir=./dist/v{parse_version(VERSION).major}/{VERSION}/')


def commit(message: str = f'New Commit at {datetime.now()}'):
    """
    Commits files to local repository.
    """
    system(f'git commit -m "{message}" -a')


def upload_testpypi(version: str = VERSION):
    """
    Uploads the project to PyPi's test server.
    :param version: The specific version to upload.
    """
    system(f'twine upload --username __token__ --password {TOKEN} --repository testpypi dist/psg_reskinner-{version}*')


def upload_legacy(version: str = VERSION):
    """
    Uploads the project to PyPi's legacy servers.
    :param version: The specific version to upload.
    """
    system(f'twine upload --username __token__ --password {TOKEN} --repository-url https://upload.pypi.org/legacy/ dist/psg_reskinner-{version}*')


def bumpver(major: bool = False, minor: bool = False, patch: bool = True):
    """
    Internal use only.

    Bumps the version a notch using the BumpVer tool.
    """
    if sum([major, minor, patch]) != 1:
        raise Exception('One (and only one) of major, minor or patch must be set!')
    target = 'major' if major else 'minor' if minor else 'patch'
    system(f'bumpver update --{target}')


def update_demo():
    """
    Internal use only.

    Updates the README with the demo code.
    """
    system('python demo_updater.py')


update_demo()
commit()
bumpver()
# build()
'''
def _main():
    """
    Internal use only.

    Handles the CLI for the script.

    Runs when the script is run.

    """
    parser = p()
    parser.add_argument('task',
                        help='Defines what the script will do; \'build\', \'upload\' or \'complete\' (does both).')
    parser.add_argument('--upload_to',
                        help='Where to upload the distro to. '
                             'Should either be \'test\' (to upload to test PyPi) or \'legacy\'. '
                             f'Defaults to {DEFAULT_UPLOAD_DESTINATION}.'
                             'Useful when building.')
    args = parser.parse_args()
    if args.task:
        if args.task == 'build' or args.task == 'complete':
            build()
        if args.task == 'upload' or args.task == 'complete':
            if not args.upload_to:
                args.upload_to = DEFAULT_UPLOAD_DESTINATION
            if args.upload_to == 'test':
                upload_testpypi()
            elif args.upload_to == 'legacy':
                upload_legacy()

_main()
'''


