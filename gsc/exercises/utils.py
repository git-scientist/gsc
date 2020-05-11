import os
import stat
import shutil
import subprocess
import typing as t
from gsc import cli, verifier


def pluralise_commits(number: str) -> str:
    if number == "1":
        return "is 1 commit"
    else:
        return f"are {number} commits"


def clean_status() -> bool:
    res = subprocess.run(["git", "status", "--porcelain"], capture_output=True)
    return res.stdout.decode("utf-8").strip() == ""


def on_branch(branch: str) -> bool:
    res = subprocess.run(["git", "branch"], capture_output=True)
    return b"* " + branch.encode("utf-8") in res.stdout


def tests_pass() -> bool:
    res = subprocess.run(["pytest"], capture_output=True)
    return res.returncode == 0


def assert_up_to_date_with_remote(branch: str) -> None:
    res = subprocess.run(
        ["git", "rev-list", "--left-right", "--count", f"{branch}...origin/{branch}"],
        capture_output=True,
    )
    commits = res.stdout.decode("utf-8").strip().split("\t")
    if ["0", "0"] != commits:
        raise verifier.VerifyError(
            f"There {pluralise_commits(commits[0])} on your local repo which aren't on your remote.\n"
            f"There {pluralise_commits(commits[1])} on your remote repo which aren't on your local.\n"
            "Your local and remote repos should have the same commits.\n"
            "Run `gsc reset` to try again if you aren't sure what's gone wrong."
        )


def remove_hash(msg: str) -> str:
    chunks = msg.split(" ", 1)[1:]
    return " ".join(chunks).strip()


def most_recent_commit_message() -> str:
    res = subprocess.run(["git", "log", "-1", "--oneline"], capture_output=True)
    return remove_hash(res.stdout.decode("utf-8"))


def most_recent_commit_description() -> str:
    res = subprocess.run(["git", "log", "-1", "--pretty=%B"], capture_output=True)
    commit_msg = res.stdout.decode("utf-8").strip()
    [_title, desc] = commit_msg.split("\n\n", 1)
    return desc


def commit_messages() -> t.List[str]:
    res = subprocess.run(["git", "log", "--oneline"], capture_output=True)
    msgs = res.stdout.decode("utf-8").split("\n")[:-1]
    return list(map(remove_hash, msgs))


def check_commit_message(msg: str) -> None:
    cli.info(f"Checking commit message: {msg}")

    if msg.endswith("."):
        cli.warn(
            "You shouldn't put a full stop at the end of your Git commit messages.\n"
            "Messages should be concise and not gramatically correct sentences."
        )

    if len(msg) >= 50:
        cli.warn(
            "Git commit messages should be fewer than 50 characters long.\n"
            f"You've used {len(msg)}.\n"
            "Try to make your commit messages more concise."
        )


def remove_readonly(func, path, execinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def rmtree_readonly(root):
    shutil.rmtree(root, onerror=remove_readonly)
