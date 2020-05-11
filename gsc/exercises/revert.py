import shutil
import pathlib
import subprocess

from gsc import verifier, cli, setup_exercise
from gsc.exercises import utils

REVERT_HASH = "67a6501a99ef70b8d554e2b11357740cb1f9b8a0"
FILE_NAME = "useful_things.py"


def setup():
    cli.info("There's no setup for this exercise.")


def reset():
    subprocess.run(["git", "checkout", "master"], capture_output=True)
    # Reset to origin/master
    subprocess.run(["git", "reset", "--hard", "origin/master"], capture_output=True)


def verify():
    if not utils.clean_status():
        raise verifier.VerifyError(
            "Your git status is not clean. Run `git status` to see the problem."
        )

    commit_messages = utils.commit_messages()

    # We should have 3 commits
    num_commits = len(commit_messages)
    if num_commits != 3:
        raise verifier.VerifyError(
            f"There {utils.pluralise_commits(num_commits)} on your local branch.\n"
            "There should be exactly 3: the 2 original commits and 1 revert commit.\n"
            "Run `gsc reset` to try again."
        )

    # The code should be the same as in the initial commit
    codefile = pathlib.Path(FILE_NAME)
    code = codefile.read_text()
    if (
        """
def subtract(x, y):
    return x + y"""
        not in code
    ):
        raise verifier.VerifyError(
            "You chose the wrong version of the code when fixing the conflict.\n"
            "This implementation is broken!\n"
            'Take another look at "Fix the Merge Conflict".\n'
            "Run `gsc reset` and try again."
        )

    # The revert commit title should start with the word "Revert".
    title = utils.most_recent_commit_message()
    if not title.startswith("Revert"):
        raise verifier.VerifyError(
            'The revert commit title should start with the word "Revert".\n'
            "Git does this automatically when you revert a commit - don't change it!"
        )

    # The reverted commit hash should be in the revert commit description.
    desc = utils.most_recent_commit_description()
    if REVERT_HASH not in desc:
        raise verifier.VerifyError(
            "The commit hash is not in the commit message description.\n"
            "Git puts it there automatically when you revert a commit - don't delete it!"
        )

    cli.success("Done.")
