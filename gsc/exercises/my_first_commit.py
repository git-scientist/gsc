from gsc import client
from gsc.exercises import utils


def verify():
    payload = {
        "git status --porcelain": utils.git_status(),
        "git branch": utils.git_branch(),
        "git rev-list --left-right --count master...origin/master": utils.rev_list_count_remote(
            "master"
        ),
        "git log -1 --oneline": utils.git_log_last_oneline(),
    }

    client.verify("my_first_commit", payload)
