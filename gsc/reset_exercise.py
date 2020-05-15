import os
import pathlib
from gsc import cli
from gsc.exercises import (
    sync_error,
    merge_conflict,
    multiple_remotes,
    use_the_force,
    revert,
    reset_file,
    amend,
)


class ResetError(Exception):
    pass


def reset():
    while not os.path.exists(".git"):
        os.chdir("..")
        if os.getcwd() == "/":
            raise ResetError("This is not a git repo.")

    if not os.path.exists(".gsc_id"):
        raise ResetError("This is not a Git Scientist exercise.")
    gsc_id = pathlib.Path(".gsc_id").read_text().strip()

    cli.info(f"Resetting {gsc_id}")

    if gsc_id == "sync_error":
        sync_error.reset()
    elif gsc_id == "merge_conflict":
        merge_conflict.reset()
    elif gsc_id == "multiple_remotes":
        multiple_remotes.reset()
    elif gsc_id == "use_the_force":
        use_the_force.reset()
    elif gsc_id == "revert":
        revert.reset()
    elif gsc_id == "reset_file":
        reset_file.reset()
    elif gsc_id == "amend":
        amend.reset()
    else:
        raise ResetError("Unknown Git Scientist exercise. Try upgrading gsc.")
