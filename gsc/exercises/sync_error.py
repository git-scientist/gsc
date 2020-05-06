import json
import shutil
import pathlib
import subprocess

from gsc import verifier, cli, setup_exercise
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

    res = subprocess.run(["git", "add", FILE_NAME], capture_output=True)
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to add first code change.")

    res = subprocess.run(
        ["git", "commit", "-m", REMOTE_COMMIT_MSG], capture_output=True
    )
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to commit first code change.")

    res = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True)
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to get hash of first commit.")
    state["remote_hash"] = res.stdout.decode("utf-8").strip()

    cli.info("Pushing the commit.")
    res = subprocess.run(["git", "push"], capture_output=True)
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

    res = subprocess.run(["git", "add", FILE_NAME], capture_output=True)
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to add second code change.")

    res = subprocess.run(["git", "commit", "-m", LOCAL_COMMIT_MSG], capture_output=True)
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
        ["git", "rev-list", "--max-parents=0", "HEAD"], capture_output=True
    )
    root_commit = res.stdout.decode("utf-8").strip()
    subprocess.run(["git", "reset", "--hard", root_commit], capture_output=True)
    # Force push
    cli.info("Cleaning remote repo.")
    subprocess.run(["git", "push", "--force"], capture_output=True)
    # Setup again
    cli.info("Setting up again.")
    setup()


def verify():
    if not utils.clean_status():
        raise verifier.VerifyError(
            "Your git status is not clean. Run `git status` to see the problem."
        )

    if not utils.on_branch("master"):
        raise verifier.VerifyError(
            "You should be on the master branch for this exercise.\n"
            "Change branch with `git checkout master` and try again."
        )

    state = json.loads(pathlib.Path(".gsc_state").read_text())

    # Get commit hashes
    res = subprocess.run(["git", "rev-list", "--all"], capture_output=True)
    commit_hashes = res.stdout.decode("utf-8").strip().split("\n")

    # We should have the remote commit
    if state["remote_hash"] not in commit_hashes:
        raise verifier.VerifyError(
            f'The "{REMOTE_COMMIT_MSG}" commit is missing!\n'
            "It's on the remote repo. You need to bring in into your local somehow..."
        )

    commit_messages = utils.commit_messages()
    # We should have the local commit
    if LOCAL_COMMIT_MSG not in commit_messages:
        raise verifier.VerifyError(
            f'The "{LOCAL_COMMIT_MSG}" commit is missing!\n'
            "Run `gsc reset` and try again."
        )

    # We should not have a merge commit
    if any(["Merge branch" in msg for msg in commit_messages]):
        raise verifier.VerifyError(
            "You created a merge commit when you pulled in the remote commit.\n"
            'Take another look at "How do we fix a sync error?"\n'
            "Run `gsc reset` and try again."
        )

    # We should be up to date with the remote
    utils.assert_up_to_date_with_remote("master")

    cli.success("Done.")
