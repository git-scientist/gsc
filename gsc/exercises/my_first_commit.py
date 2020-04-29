import subprocess

from gsc import verifier, cli
from gsc.exercises import utils


def verify():
    if not utils.clean_status():
        raise verifier.VerifyError(
            "Your git status is not clean. Run `git status` to see the problem."
        )

    if not utils.on_branch("master"):
        raise verifier.VerifyError(
            "You should be on the master branch for this exercise.\n"
            "Change branch with `git checkout master` and try again."
        )

    # We should be one commit ahead of remote master
    res = subprocess.run(
        ["git", "rev-list", "--left-right", "--count", "master...origin/master"],
        capture_output=True,
    )
    res = res.stdout.decode("utf-8").strip().split("\t")
    if ["1", "0"] != res:
        raise verifier.VerifyError(
            f"You need to make 1 commit but you've made {res[0]}."
        )

    # We should ideally have this exact commit message but no bother if not
    msg = utils.most_recent_commit_message()
    utils.check_commit_message(msg)
    if msg != "Switch `subtract` to use correct operator":
        cli.warn(
            "Looks like you didn't choose the suggested commit message.\n"
            'When you get to the "Useful Commit Messages" section, be sure to come back here '
            "and check that your message is good."
        )
    cli.success("Looks good.")
