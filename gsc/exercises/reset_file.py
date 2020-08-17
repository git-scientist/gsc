import json
import pathlib
import subprocess
from subprocess import PIPE

from gsc import verifier, cli, client
from gsc.exercises import utils

FILE_NAME = "useful_things.py"


def setup():
    # Make sure we're on the master branch
    subprocess.run(["git", "checkout", "master"], stdout=PIPE, stderr=PIPE)

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
    subprocess.run(["git", "checkout", "master"], stdout=PIPE, stderr=PIPE)
    # Reset to origin/master
    subprocess.run(
        ["git", "reset", "--hard", "origin/master"], stdout=PIPE, stderr=PIPE
    )
    cli.info("Setting up again.")
    setup()


def verify():
    try:
        state = json.loads(pathlib.Path(".gsc_state").read_text())
    except FileNotFoundError:
        raise verifier.VerifyError("You haven't set up the exercise.\nRun `gsc setup`.")

    commit_messages = utils.git_log_oneline()

    # The code should be the same as in the initial commit
    codefile = pathlib.Path(FILE_NAME)
    code = codefile.read_text()

    payload = {
        "git status --porcelain": utils.git_status(),
        "git branch": utils.git_branch(),
        "git log --oneline": commit_messages,
        "state": state,
        "code": code,
    }
    client.verify("reset_file", payload)
