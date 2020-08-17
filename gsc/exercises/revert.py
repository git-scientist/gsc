import pathlib
import subprocess
from subprocess import PIPE

from gsc import cli, client
from gsc.exercises import utils

REVERT_HASH = "67a6501a99ef70b8d554e2b11357740cb1f9b8a0"
FILE_NAME = "useful_things.py"


def setup():
    cli.info("There's no setup for this exercise.")


def reset():
    subprocess.run(["git", "checkout", "master"], stdout=PIPE, stderr=PIPE)
    # Reset to origin/master
    subprocess.run(
        ["git", "reset", "--hard", "origin/master"], stdout=PIPE, stderr=PIPE
    )


def verify():
    commit_messages = utils.git_log_oneline()
    codefile = pathlib.Path(FILE_NAME)
    code = codefile.read_text()

    payload = {
        "git status --porcelain": utils.git_status(),
        "git branch": utils.git_branch(),
        "git log --oneline": commit_messages,
        "git log -1 --pretty=%B": utils.git_log_last_pretty(),
        "code": code,
        "revert_hash": REVERT_HASH,
    }
    client.verify("revert", payload)
