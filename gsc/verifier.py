import os
from gsc import cli, client
import gsc.exercises.my_first_commit


class VerifyError(Exception):
    pass


def verify():
    while not os.path.exists(".git"):
        os.chdir("..")
        if os.getcwd() == "/":
            raise VerifyError("This is not a git repo.")

    if not os.path.exists(".gsc_id"):
        raise VerifyError("This repo is not a Git Scientist exercise.")

    gsc_id = open(".gsc_id", "r").read().strip()

    cli.title(f"Verifying {gsc_id}")

    if gsc_id == "my_first_commit":
        gsc.exercises.my_first_commit.verify()
        client.complete_exercise(gsc_id)
    else:
        raise VerifyError("Unknown Git Scientist exercise. Try updating gsc.")
