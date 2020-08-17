import json
import pathlib
import subprocess
from subprocess import PIPE

from gsc import verifier, cli, client, setup_exercise
from gsc.exercises import utils

MASTER_COMMIT_MSG = "Fix divide function for some numbers"
BRANCH_COMMIT_MSG = "Fix divide function for all numbers"
FILE_NAME = "useful_things.py"
BRANCH_NAME = "fix-divide"


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
    cli.info("Implementing the divide function incorrectly on master.")
    code = codefile.read_text()
    implemented_divide = code.replace(
        """
def divide(x, y):
    return "Hello World"
""",
        """
def divide(x, y):
    # This is probably correct - don't have time to test
    return x % y
""",
    )
    codefile.write_text(implemented_divide)

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

    # Push master branch
    cli.info("Pushing master.")
    res = subprocess.run(["git", "push"], stdout=PIPE, stderr=PIPE)
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to push commit.")

    # Switch branch
    cli.info("Switching branch.")
    subprocess.run(["git", "checkout", BRANCH_NAME], stdout=PIPE, stderr=PIPE)

    # Create local commit
    cli.info(f"Implementing the divide function correctly on branch `{BRANCH_NAME}`.")
    implemented_divide = code.replace(
        """
def divide(x, y):
    return "Hello World"
""",
        """
def divide(x, y):
    return x / y
""",
    )
    codefile.write_text(implemented_divide)

    res = subprocess.run(["git", "add", FILE_NAME], stdout=PIPE, stderr=PIPE)
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to add code change to branch.")

    res = subprocess.run(
        ["git", "commit", "-m", BRANCH_COMMIT_MSG], stdout=PIPE, stderr=PIPE
    )
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to commit to branch.")

    # Push local branch
    cli.info(f"Pushing {BRANCH_NAME}.")
    res = subprocess.run(
        ["git", "push", "--set-upstream", "origin", BRANCH_NAME],
        stdout=PIPE,
        stderr=PIPE,
    )
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to push commit.")

    # Back to master
    cli.info("Switching back to master.")
    subprocess.run(["git", "checkout", "master"], stdout=PIPE, stderr=PIPE)

    # Stash master commit hash for verification later
    pathlib.Path(".gsc_state").write_text(json.dumps(state))

    cli.info(
        "\nUse `git status`, `git log`, and `git branch` to take a look at what's changed in your local repo.\n"
        f"When you're ready to start, rebase the `{BRANCH_NAME}` branch onto master and push it.\n"
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
    # Force push master
    cli.info("Resetting remote master.")
    subprocess.run(["git", "push", "--force"], stdout=PIPE, stderr=PIPE)
    # Delete branch
    cli.info(f"Removing branch `{BRANCH_NAME}`.")
    subprocess.run(["git", "branch", "-D", BRANCH_NAME], stdout=PIPE, stderr=PIPE)
    # Delete remote branch
    cli.info(f"Removing remote branch `{BRANCH_NAME}`.")
    subprocess.run(
        ["git", "push", "-d", "origin", BRANCH_NAME], stdout=PIPE, stderr=PIPE
    )
    # Setup again
    cli.info("Setting up again.")
    setup()


def verify():
    # TODO: this should be sorted out properly.
    # See merge_conflict.py
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
        "git rev-list --left-right --count": utils.rev_list_count_remote(BRANCH_NAME),
        "branch_name": BRANCH_NAME,
        "state": state,
        "git log --format=%H": commit_hashes,
        "git log --oneline": commit_messages,
        "master_commit_message": MASTER_COMMIT_MSG,
        "branch_commit_message": BRANCH_COMMIT_MSG,
        "code": code,
    }
    client.verify("use_the_force", payload)
