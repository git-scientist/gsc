import pathlib
import subprocess
from subprocess import PIPE

from gsc import cli, setup_exercise, client
from gsc.exercises import utils

FILE_NAME = "useful_things.py"
MASTER_COMMIT_MSG = "Fix the subtract function"


def setup():
    # Make sure we're on the master branch
    subprocess.run(["git", "checkout", "master"], stdout=PIPE, stderr=PIPE)

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

    res = subprocess.run(["git", "add", FILE_NAME], stdout=PIPE, stderr=PIPE)
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to add code change to master.")

    res = subprocess.run(
        ["git", "commit", "-m", MASTER_COMMIT_MSG], stdout=PIPE, stderr=PIPE
    )
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to commit to master.")

    cli.info(
        "\nUse `git status` and `git log` to take a look at what's changed in your local repo.\n"
        "When you're ready to start, amend the most recent commit.\n"
    )


def reset():
    subprocess.run(["git", "checkout", "master"], stdout=PIPE, stderr=PIPE)
    subprocess.run(
        ["git", "reset", "--hard", "origin/master"], stdout=PIPE, stderr=PIPE
    )
    cli.info("Setting up again.")
    setup()


def verify():
    commit_messages = utils.git_log_oneline()
    codefile = pathlib.Path(FILE_NAME)
    code = codefile.read_text()

    payload = {
        "git status --porcelain": utils.git_status(),
        "git branch": utils.git_branch(),
        "git log --oneline": commit_messages,
        "code": code,
    }
    client.verify("amend", payload)
