import os
from gsc import cli
import gsc.exercises.push_and_pull


class SetupError(Exception):
    pass


def setup(gsc_id: str):
    while not os.path.exists(".git"):
        os.chdir("..")
        if os.getcwd() == "/":
            raise SetupError("This is not a git repo.")

    # Just in case someone decides to use dashes.
    gsc_id = gsc_id.replace("-", "_")

    cli.info(f"Setting up {gsc_id}")

    if gsc_id == "push_and_pull":
        gsc.exercises.push_and_pull.setup()
    else:
        raise SetupError("Unknown Git Scientist exercise. Try updating gsc.")
