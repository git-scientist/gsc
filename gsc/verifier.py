import os
import pathlib
from gsc import cli, client
import gsc.exercises.my_first_commit, gsc.exercises.push_and_pull, gsc.exercises.ssh_clone
import gsc.exercises.sync_error, gsc.exercises.merge_conflict


class VerifyError(Exception):
    pass


def verify(exercise: str = None):
    while not os.path.exists(".git"):
        os.chdir("..")
        if os.getcwd() == "/":
            raise VerifyError("This is not a git repo.")

    if exercise == "ssh":
        cli.title(f"Verifying ssh")
        gsc.exercises.ssh_clone.verify()
        client.complete_exercise("ssh_clone")
        return
    elif exercise:
        raise VerifyError("Unknown Git Scientist exercise. Try upgrading gsc.")

    if os.getcwd().endswith(gsc.exercises.push_and_pull.PULL_SUFFIX):
        gsc_id = "push_and_pull"
    elif not os.path.exists(".gsc_id"):
        raise VerifyError("This repo is not a Git Scientist exercise.")
    else:
        gsc_id = pathlib.Path(".gsc_id").read_text().strip()

    cli.title(f"Verifying {gsc_id}")

    if gsc_id == "my_first_commit":
        gsc.exercises.my_first_commit.verify()
        client.complete_exercise(gsc_id)
    elif gsc_id == "push_and_pull":
        gsc.exercises.push_and_pull.verify()
        client.complete_exercise(gsc_id)
    elif gsc_id == "sync_error":
        gsc.exercises.sync_error.verify()
        client.complete_exercise(gsc_id)
    elif gsc_id == "merge_conflict":
        gsc.exercises.merge_conflict.verify()
        client.complete_exercise(gsc_id)
    else:
        raise VerifyError("Unknown Git Scientist exercise. Try upgrading gsc.")
