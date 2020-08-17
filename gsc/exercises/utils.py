import os
import stat
import shutil
import subprocess
from subprocess import PIPE


def git_status() -> str:
    res = subprocess.run(["git", "status", "--porcelain"], stdout=PIPE, stderr=PIPE)
    return parse(res)


def mid_rebase() -> bool:
    return "no branch, rebasing" in git_branch()


def git_branch() -> str:
    res = subprocess.run(["git", "branch"], stdout=PIPE, stderr=PIPE)
    return parse(res)


def git_remote() -> str:
    res = subprocess.run(["git", "remote", "-v"], stdout=PIPE, stderr=PIPE)
    return parse(res)


def rev_list_count_remote(branch: str) -> str:
    res = subprocess.run(
        ["git", "rev-list", "--left-right", "--count", f"{branch}...origin/{branch}"],
        stdout=PIPE,
        stderr=PIPE,
    )
    return parse(res)


def git_log_last_oneline() -> str:
    res = subprocess.run(["git", "log", "-1", "--oneline"], stdout=PIPE, stderr=PIPE)
    return parse(res)


def git_log_last_pretty() -> str:
    res = subprocess.run(["git", "log", "-1", "--pretty=%B"], stdout=PIPE, stderr=PIPE)
    return parse(res)


def git_log_oneline() -> str:
    res = subprocess.run(["git", "log", "--oneline"], stdout=PIPE, stderr=PIPE)
    return parse(res)


def git_log_oneline_remote() -> str:
    res = subprocess.run(
        ["git", "log", "--oneline", "origin/master"], stdout=PIPE, stderr=PIPE
    )
    return parse(res)


def git_log_hashes() -> str:
    res = subprocess.run(["git", "log", "--format=%H"], stdout=PIPE, stderr=PIPE)
    return parse(res)


def remove_readonly(func, path, execinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def rmtree_readonly(root):
    shutil.rmtree(root, onerror=remove_readonly)


def parse(res) -> str:
    return res.stdout.decode("utf-8").strip()
