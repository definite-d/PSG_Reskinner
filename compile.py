"""
Compile Script.
Performs the jobs for compling Reskinner.

Since this project was primarily built on Windows, this script is 
guaranteed to work for Windows compilation, but it "should" work on 
other platforms (Mac and Linux).

The configuration functions are at the bottom of the script, 
if modification is required.

Compilation in general requires the `black` and `isort` libraries, 
and a working install of `git`.
"""

import re
from datetime import datetime
from inspect import getsourcelines
from os import system as run, environ as env
from pathlib import Path

from dotenv import load_dotenv
from semver import Version

from psg_reskinner.psg_reskinner import main
from psg_reskinner.version import __version__ as VERSION

print("Starting the Compiler Script...")
load_dotenv()


# SOURCE_FOLDER = Path("./psg_reskinner copy")
SOURCE_FOLDER = Path("./psg_reskinner")
DEFAULT_UPLOAD_DESTINATION = "legacy"
DEFAULT_OUTPUT_DIR = f"dist/v{Version.parse(VERSION).major}/{VERSION}"
print(DEFAULT_OUTPUT_DIR)

DRY_README_PATH = "./res/README_DRY.md"
README_PATH = "./README.md"
START_DEMO = "# % START DEMO % #"
END_DEMO = "# % END DEMO % #"

TOKEN = env.get("COMPILE_SCRIPT_PYPI_ACCESS_TOKEN")


def update_demo():
    print("Updating Demo Code in main README.", end="")

    print("\rObtaining demo code from main function...", end="")

    # Change the newlines on each line to literal slashes and n's, eliminate indents and join those lines
    # back together.
    source = "".join(
        [
            "".join(str(line).replace("\n", r"\n").split("    ", maxsplit=1))
            for line in getsourcelines(main)[0]
        ]
    )
    demo_code_pattern = re.compile(rf"{START_DEMO}.*{END_DEMO}")

    # We're doing some crazy RegEx magic here, but basically we find the start and end points of the demo,
    # get the string from that start to end, remove the start and end indicators (and their newlines,
    # which now take up 2 characters because we converted them to r initially) and change the newlines
    # back to their original form.
    demo_lines = (
        re.search(demo_code_pattern, source)
        .group(0)[len(START_DEMO) + 4 : -(len(END_DEMO) + 2)]
        .replace(r"\n", "\n")
    )

    # Then the hydration occurs.
    with open(DRY_README_PATH, "r") as readme:
        print("\rReading dry README file...", end="")
        data = readme.read()
        pattern = re.compile(f"# Demo code goes here. Run the update to hydrate it.")
        print("\rConstructing new README...", end="")
        new_data = re.sub(pattern, demo_lines, data)
    with open(README_PATH, "w") as out:
        # And done.
        print("\rWriting new README to file...", end="")
        out.write(new_data)
        print("\rREADME updated successfully with demo code from main().")


def run_formatting(filepath):
    run(f'isort "{filepath}" --quiet')
    run(f'black "{filepath}" --quiet')


def format_source_files():
    for file_ in Path(SOURCE_FOLDER).glob("*.py"):
        print(f"Formatting {file_}...")
        update_copyright_year(file_)
        run_formatting(file_)


def bumpver(major: bool = False, minor: bool = False, patch: bool = True):
    """
    Internal use only.

    Bumps the version a notch using the BumpVer tool.
    """
    print("Updating version...")
    if sum([major, minor, patch]) != 1:
        raise Exception("One (and only one) of major, minor or patch must be set!")
    target = "major" if major else "minor" if minor else "patch"
    run(f"bumpver update --{target}")


def git_commit(message: str = f"New commit at {datetime.now()}"):
    print("Staging commit...")
    run(f'git commit -m "{message}" -a')
    print("Commit completed successfully.")


def build():
    """
    Builds the project.
    """
    print("Building...")
    run(
        f"python "
        f"-m "
        f"build "
        # f"-n "
        f"--outdir=./{DEFAULT_OUTPUT_DIR}/"
    )


def upload_testpypi(version: str = VERSION):
    """
    Uploads the project to PyPi's test server.
    :param version: The specific version to upload.
    """
    print("Uploading to TestPyPi...")
    run(
        f"twine upload --username __token__ --password {TOKEN} --repository testpypi {DEFAULT_OUTPUT_DIR}/psg_reskinner-{version}*"
    )


def upload_legacy(version: str = VERSION):
    """
    Uploads the project to PyPi's legacy servers.
    :param version: The specific version to upload.
    """
    print("Uploading to PyPi...")
    run(
        f"twine upload --username __token__ --password {TOKEN} --repository-url https://upload.pypi.org/legacy/ {DEFAULT_OUTPUT_DIR}/psg_reskinner-{version}*"
    )


def update_copyright_year(filepath: str):
    pattern = re.compile(r"Copyright \(c\) [0-9]* Afam\-Ifediogor Divine\.")
    replacement = rf"Copyright (c) {datetime.now().year} Afam-Ifediogor Divine."

    with open(filepath, "r") as _file:
        content = _file.read().replace("\n", r"\n")
        content = re.sub(pattern, replacement, content)
        content = content.replace(r"\n", "\n")

    with open(filepath, "w") as _file:
        _file.write(content)


# The following lines are the main controls to this script. Comment and uncomment as desired, but do not change the order.

update_demo()
bumpver()
# format_source_files()
# build()
# git_commit()
# upload_legacy()
print("compile.py has completed execution.")
