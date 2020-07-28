import subprocess
from subprocess import PIPE

from gsc import verifier, cli


def verify():
    res = subprocess.run(["git", "remote", "-v"], stdout=PIPE, stderr=PIPE)
    res = res.stdout.decode("utf-8").strip()

    if "git@github.com:" not in res:
        raise verifier.VerifyError("Repo not cloned using SSH.")

    cli.success("Looks good.")
