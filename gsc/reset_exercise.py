import os
import pathlib
from gsc import cli
import gsc.exercises.sync_error, gsc.exercises.merge_conflict


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
        gsc.exercises.sync_error.reset()
    if gsc_id == "merge_conflict":
        gsc.exercises.merge_conflict.reset()
    else:
        raise ResetError("Unknown Git Scientist exercise. Try upgrading gsc.")
