import os
from gsc import cli, client
import gsc.exercises.my_first_commit, gsc.exercises.push_and_pull, gsc.exercises.ssh_clone


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
        raise VerifyError("Unknown Git Scientist exercise. Try updating gsc.")

    if os.getcwd().endswith(gsc.exercises.push_and_pull.PULL_SUFFIX):
        # Special case if we haven't pulled the commit which adds .gsc_id
        # Verify should fail. Raise if it somehow doesn't.
        cli.title(f"Verifying push_and_pull")
        gsc.exercises.push_and_pull.verify()
        raise VerifyError("This should never happen. Contact us.")

    if not os.path.exists(".gsc_id"):
        raise VerifyError("This repo is not a Git Scientist exercise.")

    gsc_id = open(".gsc_id", "r").read().strip()

    cli.title(f"Verifying {gsc_id}")

    if gsc_id == "my_first_commit":
        gsc.exercises.my_first_commit.verify()
        client.complete_exercise(gsc_id)
    elif gsc_id == "push_and_pull":
        gsc.exercises.push_and_pull.verify()
        client.complete_exercise(gsc_id)
    else:
        raise VerifyError("Unknown Git Scientist exercise. Try updating gsc.")
