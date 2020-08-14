import os
import typer
import shutil
import subprocess
from subprocess import PIPE

from gsc import cli, client, setup_exercise
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

    res = subprocess.run(["git", "add", ".gsc_id"], stdout=PIPE, stderr=PIPE)
    if res.returncode != 0:
        raise setup_exercise.SetupError("Failed to add gsc_id. Contact us for help.")

    res = subprocess.run(["git", "commit", "-m", COMMIT_MSG], stdout=PIPE, stderr=PIPE)
    if res.returncode != 0:
        raise setup_exercise.SetupError(
            "Failed to setup Git Scientist. Contact us for help."
        )


def verify():
    cwd = os.getcwd()
    if cwd.endswith(PULL_SUFFIX):
        repo_name = cwd[: -len(PULL_SUFFIX)]
        pull_repo_name = cwd
    else:
        repo_name = cwd
        pull_repo_name = cwd + PULL_SUFFIX

    os.chdir(repo_name)
    remote_commit_messages = utils.git_log_oneline_remote()
    main_commit_messages = utils.git_log_oneline()

    os.chdir(pull_repo_name)
    pull_commit_messages = utils.git_log_oneline()

    payload = {
        "git status --porcelain": utils.git_status(),
        "git branch": utils.git_branch(),
        "git log --oneline origin/master": remote_commit_messages,
        "main:git log --oneline": main_commit_messages,
        "pull:git log --oneline": pull_commit_messages,
        "pull_repo_name": pull_repo_name,
        "expect_msg": COMMIT_MSG,
    }
    client.verify("push_and_pull", payload)
