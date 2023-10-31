"""
Build script for psg_reskinner.
"""
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

from datetime import datetime
from os.path import abspath, split, sep
from subprocess import run

from import_util import import_by_file

psg_reskinner = import_by_file("psg_reskinner", "../")

VERSION = psg_reskinner.version.__version__
major, minor, patch = map(lambda x: int(x), VERSION.split("."))
print(f"Working with Reskinner v{VERSION}.")

DEFAULT_UPLOAD_DESTINATION = "legacy"
DEFAULT_OUTPUT_DIR = f"dist/v{major}/{VERSION}"
FILE_DIR = abspath(split(__file__)[0])
WORKING_DIR = abspath(FILE_DIR.rsplit(sep, 1)[0])

with open(f"{FILE_DIR}/.env", "r") as env:
    TOKEN = env.readline()


def build():
    """
    Builds the project.
    """
    print("Building...")
    run(f"python -m build -n --outdir=./{DEFAULT_OUTPUT_DIR}/", cwd=WORKING_DIR)


def commit(message: str = f"New Commit at {datetime.now()}"):
    """
    Commits files to local repository.
    """
    print("Staging commit...")
    run(f'git commit -m "{message}" -a', cwd=WORKING_DIR)
    print("Commit completed successfully.")


def upload_testpypi(version: str = VERSION):
    """
    Uploads the project to PyPi's test server.
    :param version: The specific version to upload.
    """
    print("Uploading to TestPyPi...")
    run(
        f"twine upload --username __token__ --password {TOKEN} --repository testpypi {DEFAULT_OUTPUT_DIR}/psg_reskinner-{version}*",
        cwd=WORKING_DIR,
    )


def upload_legacy(version: str = VERSION):
    """
    Uploads the project to PyPi's legacy servers.
    :param version: The specific version to upload.
    """
    print("Uploading to PyPi...")
    run(
        f"twine upload --username __token__ --password {TOKEN} --repository-url https://upload.pypi.org/legacy/ {DEFAULT_OUTPUT_DIR}/psg_reskinner-{version}*",
        cwd=WORKING_DIR,
    )


def bumpver(major: bool = False, minor: bool = False, patch: bool = True):
    """
    Internal use only.

    Bumps the version a notch using the BumpVer tool.
    """
    print("Updating version...")
    if sum([major, minor, patch]) != 1:
        raise Exception("One (and only one) of major, minor or patch must be set!")
    target = "major" if major else "minor" if minor else "patch"
    run(f"bumpver update --{target}", cwd=WORKING_DIR)


def update_demo():
    """
    Internal use only.

    Updates the README with the demo code.
    """
    run("python demo_updater.py")


def update_description_year():
    """
    Internal use only.

    Updates the copyright year of the DESCRIPTION.
    """
    run("python description_year_updater.py")


update_demo()
update_description_year()
# commit()
bumpver()
build()
# upload_legacy()
