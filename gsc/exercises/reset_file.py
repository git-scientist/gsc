import json
import shutil
import pathlib
import subprocess

from gsc import verifier, cli, setup_exercise
from gsc.exercises import utils

FILE_NAME = "useful_things.py"


def setup():
    # Make sure we're on the master branch
    subprocess.run(["git", "checkout", "master"], capture_output=True)

    # Make an uncommitted file change
    codefile = pathlib.Path(FILE_NAME)
    code = codefile.read_text()
    silly_change = code.replace(
        """
def subtract(x, y):
    return x - y
""",
        """
def subtract(x, y):
    return "Oops I should not have done this"
""",
    )
    codefile.write_text(silly_change)

    state = {"setup": True}
    pathlib.Path(".gsc_state").write_text(json.dumps(state))


def reset():
    subprocess.run(["git", "checkout", "master"], capture_output=True)
    # Reset to origin/master
    subprocess.run(["git", "reset", "--hard", "origin/master"], capture_output=True)
    cli.info("Setting up again.")
    setup()


def verify():
    try:
        pathlib.Path(".gsc_state").read_text()
    except FileNotFoundError:
        raise verifier.VerifyError("You haven't set up the exercise.\nRun `gsc setup`.")

    if not utils.clean_status():
        raise verifier.VerifyError(
            "Your git status is not clean. Run `git status` to see the problem."
        )

    # We should have 1 commit
    commit_messages = utils.commit_messages()
    num_commits = len(commit_messages)
    if num_commits != 1:
        raise verifier.VerifyError(
            f"There {utils.pluralise_commits(num_commits)} on your local branch.\n"
            "There should be exactly 1: the inital commit.\n"
            "Run `gsc reset` to try again."
        )

    # The code should be the same as in the initial commit
    codefile = pathlib.Path(FILE_NAME)
    code = codefile.read_text()
    if (
        """
def subtract(x, y):
    return x - y"""
        not in code
    ):
        raise verifier.VerifyError(
            "The code is not the same as it was originally.\n"
            "You've done something strange. Email us for help if you're not sure what.\n"
            "Run `gsc reset` and try again."
        )

    cli.success("Done.")
