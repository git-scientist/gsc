import os
import typer
import shutil
import subprocess

from gsc import verifier, cli, setup_exercise
from gsc.exercises import utils

COMMIT_MSG = "Setup Git Scientist Exercise"
PULL_SUFFIX = "-gsc-pull"


def setup():
    # Copy repo so we can practice pulling.
    repo_name = os.getcwd()
    pull_repo_name = repo_name + PULL_SUFFIX

    if os.path.exists(pull_repo_name):
        delete = typer.confirm(
            f"The directory {pull_repo_name} already exists. Do you want to delete it?"
        )
        if not delete:
            cli.info("Not deleting.")
            raise typer.Abort()
        cli.info(f"Deleting {pull_repo_name}.")
        utils.rmtree_readonl(pull_repo_name)

    shutil.copytree(repo_name, pull_repo_name)

    # Setup original repo so we can practice pushing.
    with open(".gsc_id", "w") as f:
        f.write("push_and_pull")

    res = subprocess.run(["git", "add", ".gsc_id"], capture_output=True)
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to add gsc_id. Contact us for help.")

    res = subprocess.run(["git", "commit", "-m", COMMIT_MSG], capture_output=True)
    if res.returncode != 0:
        raise setup_exercise.SetupError(
            "Failed to setup Git Scientist. Contact us for help."
        )


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

    cwd = os.getcwd()
    if cwd.endswith(PULL_SUFFIX):
        repo_name = cwd[: -len(PULL_SUFFIX)]
        pull_repo_name = cwd
    else:
        repo_name = cwd
        pull_repo_name = cwd + PULL_SUFFIX

    # Check that both repos contain the commit we want.
    os.chdir(repo_name)
    msgs = utils.commit_messages()
    if COMMIT_MSG not in msgs:
        raise verifier.VerifyError(
            "Setup commit not found. Did you run `gsc setup push_and_pull`?"
        )

    os.chdir(pull_repo_name)
    msgs = utils.commit_messages()
    if COMMIT_MSG not in msgs:
        raise verifier.VerifyError(
            "The commit has not been pulled into your local repo.\n"
            f"The repo is located at {pull_repo_name}\n"
            "See the My First Pull section of the lesson."
        )

    cli.success("Done.")
