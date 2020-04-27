import subprocess

from gsc import verifier, cli


def verify():
    res = subprocess.run(["git", "remote", "-v"], capture_output=True)
    res = res.stdout.decode("utf-8").strip()

    if "git@github.com:" not in res:
        raise verifier.VerifyError("Repo not cloned using SSH.")

    cli.success("Looks good.")
