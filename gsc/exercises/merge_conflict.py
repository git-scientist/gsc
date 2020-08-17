import json
import pathlib
import subprocess
from subprocess import PIPE

from gsc import verifier, cli, client, setup_exercise
from gsc.exercises import utils

MASTER_COMMIT_MSG = "Fix subtract function for some numbers"
BRANCH_COMMIT_MSG = "Fix subtract function for all numbers"
FILE_NAME = "useful_things.py"
BRANCH_NAME = "fix-subtract"


def setup():
    state = {}
    # Make sure we're on the master branch
    subprocess.run(["git", "checkout", "master"], stdout=PIPE, stderr=PIPE)
    # Create branch
    res = subprocess.run(["git", "branch", BRANCH_NAME], stdout=PIPE, stderr=PIPE)
    if res.returncode != 0:
        raise setup_exercise.SetupError(
            f"Failed to create branch `{BRANCH_NAME}`. Run `gsc reset`."
        )

    codefile = pathlib.Path(FILE_NAME)

    # Create commit on master
    cli.info("Implementing the subtract function incorrectly on master.")
    code = codefile.read_text()
    implemented_subtract = code.replace(
        """
def subtract(x, y):
    return x + y
""",
        """
def subtract(x, y):
    if x > 0:
        return x - y
    return x + y
""",
    )
    codefile.write_text(implemented_subtract)

    res = subprocess.run(["git", "add", FILE_NAME], stdout=PIPE, stderr=PIPE)
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to add code change to master.")

    res = subprocess.run(
        ["git", "commit", "-m", MASTER_COMMIT_MSG], stdout=PIPE, stderr=PIPE
    )
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to commit to master.")

    res = subprocess.run(["git", "rev-parse", "HEAD"], stdout=PIPE, stderr=PIPE)
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to get hash of commit on master.")
    state["master_hash"] = res.stdout.decode("utf-8").strip()

    # Switch branch
    cli.info("Switching branch.")
    subprocess.run(["git", "checkout", BRANCH_NAME], stdout=PIPE, stderr=PIPE)

    # Create local commit
    cli.info(f"Implementing the subtract function correctly on branch `{BRANCH_NAME}`.")
    implemented_subtract = code.replace(
        """
def subtract(x, y):
    return x + y
""",
        """
def subtract(x, y):
    return x - y
""",
    )
    codefile.write_text(implemented_subtract)

    res = subprocess.run(["git", "add", FILE_NAME], stdout=PIPE, stderr=PIPE)
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to add code change to branch.")

    res = subprocess.run(
        ["git", "commit", "-m", BRANCH_COMMIT_MSG], stdout=PIPE, stderr=PIPE
    )
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to commit to branch.")

    cli.info("Switching back to master.")
    subprocess.run(["git", "checkout", "master"], stdout=PIPE, stderr=PIPE)

    # Stash master commit hash for verification later
    pathlib.Path(".gsc_state").write_text(json.dumps(state))

    cli.info(
        "\nUse `git status`, `git log`, and `git branch` to take a look at what's changed in your local repo.\n"
        "When you're ready to start the exercise, switch to the `fix-subtract` branch and try to rebase onto master.\n"
    )


def reset():
    subprocess.run(["git", "checkout", "master"], stdout=PIPE, stderr=PIPE)
    # Reset back to inital commit.
    cli.info("Rewinding history.")
    res = subprocess.run(
        ["git", "rev-list", "--max-parents=0", "HEAD"], stdout=PIPE, stderr=PIPE
    )
    root_commit = res.stdout.decode("utf-8").strip()
    subprocess.run(["git", "reset", "--hard", root_commit], stdout=PIPE, stderr=PIPE)
    # Delete branch
    cli.info(f"Removing branch `{BRANCH_NAME}`.")
    subprocess.run(["git", "branch", "-D", BRANCH_NAME], stdout=PIPE, stderr=PIPE)
    # Setup again
    cli.info("Setting up again.")
    setup()


def verify():
    # TODO: this should be sorted out properly.
    # We can run git log on the correct branch.
    # We can check out the file from the correct branch as long as we back it up and restore it
    # after.
    # Then we won't need to change branch.
    # If we're still in the middle of the merge conflict we won't be able to change branch
    if utils.mid_rebase():
        raise verifier.VerifyError(
            "You haven't finished rebasing yet. Run `git status` to see what to do next."
        )

    state = json.loads(pathlib.Path(".gsc_state").read_text())

    # We should have the branch
    res = subprocess.run(["git", "checkout", BRANCH_NAME], stdout=PIPE, stderr=PIPE)
    if res.returncode != 0:
        raise verifier.VerifyError(
            f'The "{BRANCH_NAME}" branch has been deleted!\n'
            "Run `gsc reset` to start again."
        )

    commit_hashes = utils.git_log_hashes()
    commit_messages = utils.git_log_oneline()

    codefile = pathlib.Path(FILE_NAME)
    code = codefile.read_text()

    payload = {
        "git status --porcelain": utils.git_status(),
        "git branch": utils.git_branch(),
        "branch_name": BRANCH_NAME,
        "state": state,
        "git log --format=%H": commit_hashes,
        "git log --oneline": commit_messages,
        "master_commit_message": MASTER_COMMIT_MSG,
        "branch_commit_message": BRANCH_COMMIT_MSG,
        "code": code,
    }
    client.verify("merge_conflict", payload)
