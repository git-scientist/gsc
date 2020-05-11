import shutil
import pathlib
import subprocess

from gsc import verifier, cli, setup_exercise
from gsc.exercises import utils

FILE_NAME = "useful_things.py"
MASTER_COMMIT_MSG = "Fix the subtract function"


def setup():
    # Make sure we're on the master branch
    subprocess.run(["git", "checkout", "master"], capture_output=True)

    # Commit a change which needs to be amended
    codefile = pathlib.Path(FILE_NAME)
    code = codefile.read_text()
    changed = code.replace(
        """
def subtract(x, y):
    return x + y
""",
        """
def subtract(x, y):
    # TODO: delete this comment
    return x - y
""",
    )
    codefile.write_text(changed)

    res = subprocess.run(["git", "add", FILE_NAME], capture_output=True)
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to add code change to master.")

    res = subprocess.run(
        ["git", "commit", "-m", MASTER_COMMIT_MSG], capture_output=True
    )
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to commit to master.")

    cli.info(
        "\nUse `git status` and `git log` to take a look at what's changed in your local repo.\n"
        "When you're ready to start, amend the most recent commit.\n"
    )


def reset():
    subprocess.run(["git", "checkout", "master"], capture_output=True)
    subprocess.run(["git", "reset", "--hard", "origin/master"], capture_output=True)
    cli.info("Setting up again.")
    setup()


def verify():
    if not utils.clean_status():
        raise verifier.VerifyError(
            "Your git status is not clean. Run `git status` to see the problem."
        )

    # We should have 2 commit
    commit_messages = utils.commit_messages()
    num_commits = len(commit_messages)
    if num_commits != 2:
        raise verifier.VerifyError(
            f"There {utils.pluralise_commits(num_commits)} on your local branch.\n"
            "There should be exactly 2: the inital commit and the amended commit.\n"
            "Run `gsc reset` to try again."
        )

    # The comment should be gone
    codefile = pathlib.Path(FILE_NAME)
    code = codefile.read_text()
    if "TODO" in code:
        raise verifier.VerifyError(
            "You don't seem to have amended the commit.\n"
            "Check the exercise description."
        )

    # The code should be correct
    codefile = pathlib.Path(FILE_NAME)
    code = codefile.read_text()
    if (
        """
def subtract(x, y):
    return x - y"""
        not in code
    ):
        raise verifier.VerifyError(
            "The code is no longer correct.\n"
            "Make sure you don't delete or replace working code when you amend the commit!\n"
            "Run `gsc reset` and try again."
        )

    cli.success("Done.")
