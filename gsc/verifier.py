import os
import pathlib
from gsc import cli
from gsc.exercises import (
    my_first_commit,
    push_and_pull,
    ssh_clone,
    sync_error,
    merge_conflict,
    multiple_remotes,
    use_the_force,
    revert,
    reset_file,
    amend,
)


class VerifyError(Exception):
    pass


def verify(exercise: str = None):
    while not os.path.exists(".git"):
        os.chdir("..")
        if os.getcwd() == "/":
            raise VerifyError("This is not a git repo.")

    if exercise == "ssh":
        cli.title("Verifying ssh")
        ssh_clone.verify()
        return
    elif exercise:
        raise VerifyError("Unknown Git Scientist exercise. Try upgrading gsc.")

    if os.getcwd().endswith(push_and_pull.PULL_SUFFIX):
        gsc_id = "push_and_pull"
    elif not os.path.exists(".gsc_id"):
        raise VerifyError("This repo is not a Git Scientist exercise.")
    else:
        gsc_id = pathlib.Path(".gsc_id").read_text().strip()

    cli.title(f"Verifying {gsc_id}")

    if gsc_id == "my_first_commit":
        my_first_commit.verify()
    elif gsc_id == "push_and_pull":
        push_and_pull.verify()
    elif gsc_id == "sync_error":
        sync_error.verify()
    elif gsc_id == "merge_conflict":
        merge_conflict.verify()
    elif gsc_id == "multiple_remotes":
        multiple_remotes.verify()
    elif gsc_id == "use_the_force":
        use_the_force.verify()
    elif gsc_id == "revert":
        revert.verify()
    elif gsc_id == "reset_file":
        reset_file.verify()
    elif gsc_id == "amend":
        amend.verify()
    else:
        raise VerifyError("Unknown Git Scientist exercise. Try upgrading gsc.")
