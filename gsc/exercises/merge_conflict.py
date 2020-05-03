import json
import shutil
import pathlib
import subprocess

from gsc import verifier, cli, setup_exercise
from gsc.exercises import utils

MASTER_COMMIT_MSG = "Fix subtract function for some numbers"
BRANCH_COMMIT_MSG = "Fix subtract function for all numbers"
FILE_NAME = "useful_things.py"
BRANCH_NAME = "fix-subtract"


def setup():
    state = {}
    # Make sure we're on the master branch
    subprocess.run(["git", "checkout", "master"], capture_output=True)
    # Create branch
    res = subprocess.run(["git", "branch", BRANCH_NAME], capture_output=True)
    if res.returncode != 0:
        raise setup_exercise.SetupError(
            f"Failed to create branch `{BRANCH_NAME}`. Run `gsc reset`."
        )

    codefile = pathlib.Path(FILE_NAME)

    # Create commit on master
    cli.info("Implementing the subtract incorrectly on master.")
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

    res = subprocess.run(["git", "add", FILE_NAME], capture_output=True)
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to add code change to master.")

    res = subprocess.run(
        ["git", "commit", "-m", MASTER_COMMIT_MSG], capture_output=True
    )
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to commit to master.")

    res = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True)
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to get hash of commit on master.")
    state["master_hash"] = res.stdout.decode("utf-8").strip()

    # Switch branch
    cli.info("Switching branch.")
    subprocess.run(["git", "checkout", BRANCH_NAME], capture_output=True)

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

    res = subprocess.run(["git", "add", FILE_NAME], capture_output=True)
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to add code change to branch.")

    res = subprocess.run(
        ["git", "commit", "-m", BRANCH_COMMIT_MSG], capture_output=True
    )
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to commit to branch.")

    cli.info("Switching back to master.")
    subprocess.run(["git", "checkout", "master"], capture_output=True)

    # Stash master commit hash for verification later
    pathlib.Path(".gsc_state").write_text(json.dumps(state))

    cli.info(
        "\nUse `git status`, `git log`, and `git branch` to take a look at what's changed in your local repo.\n"
        "When you're ready to start the exercise, switch to the `fix-subtract` branch and try to rebase onto master.\n"
    )


def reset():
    subprocess.run(["git", "checkout", "master"], capture_output=True)
    # Reset back to inital commit.
    cli.info("Rewinding history.")
    res = subprocess.run(
        ["git", "rev-list", "--max-parents=0", "HEAD"], capture_output=True
    )
    root_commit = res.stdout.decode("utf-8").strip()
    subprocess.run(["git", "reset", "--hard", root_commit], capture_output=True)
    # Delete branch
    cli.info(f"Removing branch `{BRANCH_NAME}`.")
    subprocess.run(["git", "branch", "-D", BRANCH_NAME], capture_output=True)
    # Setup again
    cli.info("Setting up again.")
    setup()


def pluralise(number: str) -> str:
    if number == "1":
        return "is 1 commit"
    else:
        return f"are {number} commits"


def verify():
    if not utils.clean_status():
        raise verifier.VerifyError(
            "Your git status is not clean. Run `git status` to see the problem."
        )

    state = json.loads(pathlib.Path(".gsc_state").read_text())

    # We should have the branch
    res = subprocess.run(["git", "checkout", BRANCH_NAME], capture_output=True)
    if res.returncode != 0:
        raise verifier.VerifyError(
            f'The "{BRANCH_NAME}" branch has been deleted!\n'
            "Run `gsc reset` to start again."
        )

    # Get commit hashes
    res = subprocess.run(["git", "rev-list", "--all"], capture_output=True)
    commit_hashes = res.stdout.decode("utf-8").strip().split("\n")

    # We should have the master commit
    if state["master_hash"] not in commit_hashes:
        raise verifier.VerifyError(
            f'The "{MASTER_COMMIT_MSG}" commit is missing!\n'
            f"It's on the master branch. You need to bring in into the `{BRANCH_NAME}` branch somehow..."
        )

    commit_messages = utils.commit_messages()
    # We should have the branch commit
    if BRANCH_COMMIT_MSG not in commit_messages:
        raise verifier.VerifyError(
            f'The "{BRANCH_COMMIT_MSG}" commit is missing!\n'
            "Run `gsc reset` and try again."
        )

    # We should not have a merge commit
    if any(["Merge branch" in msg for msg in commit_messages]):
        raise verifier.VerifyError(
            "You created a merge commit when you pulled in the remote commit.\n"
            'Take another look at "Exercise Setup".\n'
            "Run `gsc reset` and try again."
        )

    # We should have chosen the correct version of the code in the conflict
    codefile = pathlib.Path(FILE_NAME)
    code = codefile.read_text()
    if (
        """
def subtract(x, y):
    return x - y"""
        not in code
    ):
        raise verifier.VerifyError(
            "You chose the wrong version of the code when fixing the conflict.\n"
            "This implementation is broken!\n"
            'Take another look at "Fix the Merge Conflict".\n'
            "Run `gsc reset` and try again."
        )

    cli.success("Done.")
