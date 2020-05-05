import os
import stat
import shutil
import subprocess
import typing as t
from gsc import cli


def clean_status() -> bool:
    res = subprocess.run(["git", "status", "--porcelain"], capture_output=True)
    return res.stdout.decode("utf-8").strip() == ""


def on_branch(branch: str) -> bool:
    res = subprocess.run(["git", "branch"], capture_output=True)
    return b"* " + branch.encode("utf-8") in res.stdout


def tests_pass() -> bool:
    res = subprocess.run(["pytest"], capture_output=True)
    return res.returncode == 0


def remove_hash(msg: str) -> str:
    chunks = msg.split(" ", 1)[1:]
    return " ".join(chunks).strip()


def most_recent_commit_message() -> str:
    res = subprocess.run(["git", "log", "-1", "--oneline"], capture_output=True)
    return remove_hash(res.stdout.decode("utf-8"))


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
