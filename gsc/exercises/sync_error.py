import json
import shutil
import pathlib
import subprocess
from subprocess import PIPE

from gsc import cli, client, setup_exercise
from gsc.exercises import utils

REMOTE_COMMIT_MSG = "Implement subtract function"
LOCAL_COMMIT_MSG = "Implement divide function"
FILE_NAME = "useful_things.py"


def setup():
    state = {}
    # Backup .git
    shutil.copytree(".git", ".git.bak")

    codefile = pathlib.Path(FILE_NAME)

    # Create remote commit & push
    cli.info("Implementing the subtract function.")
    code = codefile.read_text()
    implemented_subtract = code.replace(
        """
def subtract(x, y):
    pass
""",
        """
def subtract(x, y):
    return x - y
""",
    )
    codefile.write_text(implemented_subtract)

    res = subprocess.run(["git", "add", FILE_NAME], stdout=PIPE, stderr=PIPE)
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to add first code change.")

    res = subprocess.run(
        ["git", "commit", "-m", REMOTE_COMMIT_MSG], stdout=PIPE, stderr=PIPE
    )
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to commit first code change.")

    res = subprocess.run(["git", "rev-parse", "HEAD"], stdout=PIPE, stderr=PIPE)
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to get hash of first commit.")
    state["remote_hash"] = res.stdout.decode("utf-8").strip()

    cli.info("Pushing the commit.")
    res = subprocess.run(["git", "push"], stdout=PIPE, stderr=PIPE)
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to push commit.")

    # Restore .git
    cli.info("Forgetting about remote commit.")
    utils.rmtree_readonly(".git")
    shutil.copytree(".git.bak", ".git")
    utils.rmtree_readonly(".git.bak")

    # Create local commit
    cli.info("Implementing the divide function.")
    implemented_divide = code.replace(
        """
def divide(x, y):
    pass
""",
        """
def divide(x, y):
    return x / y
""",
    )
    codefile.write_text(implemented_divide)

    res = subprocess.run(["git", "add", FILE_NAME], stdout=PIPE, stderr=PIPE)
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to add second code change.")

    res = subprocess.run(
        ["git", "commit", "-m", LOCAL_COMMIT_MSG], stdout=PIPE, stderr=PIPE
    )
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to commit second code change.")

    # Stash remote commit hash for verification later
    pathlib.Path(".gsc_state").write_text(json.dumps(state))

    cli.info(
        "\nUse `git status` and `git log` to take a look at what's changed in your local repo.\n"
        "When you're ready to start the exercise, try `git push`.\n"
    )


def reset():
    # Reset back to inital commit.
    cli.info("Rewinding history.")
    res = subprocess.run(
        ["git", "rev-list", "--max-parents=0", "HEAD"], stdout=PIPE, stderr=PIPE
    )
    root_commit = res.stdout.decode("utf-8").strip()
    subprocess.run(["git", "reset", "--hard", root_commit], stdout=PIPE, stderr=PIPE)
    # Force push
    cli.info("Cleaning remote repo.")
    subprocess.run(["git", "push", "--force"], stdout=PIPE, stderr=PIPE)
    # Setup again
    cli.info("Setting up again.")
    setup()


def verify():
    state = json.loads(pathlib.Path(".gsc_state").read_text())
    commit_hashes = utils.git_log_hashes()
    commit_messages = utils.git_log_oneline()

    payload = {
        "git status --porcelain": utils.git_status(),
        "git branch": utils.git_branch(),
        "git rev-list --left-right --count master...origin/master": utils.rev_list_count_remote(
            "master"
        ),
        "state": state,
        "git log --format=%H": commit_hashes,
        "git log --oneline": commit_messages,
        "remote_commit_message": REMOTE_COMMIT_MSG,
        "local_commit_message": LOCAL_COMMIT_MSG,
    }
    client.verify("sync_error", payload)
