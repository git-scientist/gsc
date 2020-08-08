import subprocess
from subprocess import PIPE

from gsc import verifier, cli

UPSTREAM_URL = "https://github.com/git-scientist/fork-this"
UPSTREAM_URL_GIT = UPSTREAM_URL + ".git"
UPSTREAM_SSH_URL = "git@github.com:git-scientist/fork-this"
UPSTREAM_SSH_URL_GIT = UPSTREAM_SSH_URL + ".git"


def setup():
    cli.info("There's no setup for this exercise.")


def reset():
    cli.info("There's no reset for this exercise.")


def verify():
    # We should have an origin remote with a fork url
    res = subprocess.run(["git", "remote", "-v"], stdout=PIPE, stderr=PIPE)
    if res.returncode != 0:
        raise verifier.VerifyError("Failed to list remote repos")

    remotes = {}
    res = res.stdout.decode("utf-8").strip().split("\n")
    for r in res:
        [name, url] = r.split("\t")
        [url, _] = url.split(" ")
        remotes[name] = url

    if remotes["origin"] in [
        UPSTREAM_URL,
        UPSTREAM_URL_GIT,
        UPSTREAM_SSH_URL,
        UPSTREAM_SSH_URL_GIT,
    ]:
        raise verifier.VerifyError(
            "You've cloned the upstream repo. You need to fork the repo first and then clone your fork."
        )

    num_remotes = len(remotes)
    if num_remotes == 1:
        raise verifier.VerifyError(
            "This repo only has one remote. You need to add the upstream repo as a second remote."
        )
    elif num_remotes > 2:
        raise verifier.VerifyError(
            f"This repo has {num_remotes} remotes. There should be exactly 2.\n"
            "Delete your local repo, clone your fork, and try adding the upstream remote again."
        )

    # We should have an upstream remote with the original url
    upstream = "upstream"
    if upstream not in remotes:
        remote_names = list(remotes.keys())
        remote_names.remove("origin")
        [upstream] = remote_names
        if remotes[upstream] in [
            UPSTREAM_URL,
            UPSTREAM_URL_GIT,
            UPSTREAM_SSH_URL,
            UPSTREAM_SSH_URL_GIT,
        ]:
            cli.warn(
                f'I couldn\'t find the upstream remote, but I did find a remote called "{name}" with the correct url.\n'
                'You should consider calling your upstream remotes "upstream" instead.'
            )
        else:
            raise verifier.VerifyError(
                "I couldn't find the upstream remote.\n"
                f'I found a remote called "{name}" with the wrong url.\n'
                f"{UPSTREAM_URL} is the correct url.\n"
                f"{remotes[name]} is what you have."
            )

    if remotes[upstream] in [UPSTREAM_SSH_URL, UPSTREAM_SSH_URL_GIT]:
        cli.warn(
            "You've used SSH for the upstream URL.\n"
            "There's no point using SSH for the upstream.\n"
            "You don't have write access and the repo is public, so HTTPS will do everything we need."
        )
    elif remotes[upstream] not in [UPSTREAM_URL, UPSTREAM_URL_GIT]:
        raise verifier.VerifyError(
            "The upstream url is not correct.\n"
            f"{UPSTREAM_URL} is the correct url.\n"
            f"{remotes[name]} is what you have."
        )

    cli.success("Done.")
