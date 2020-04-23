import subprocess
from gsc import cli


def clean_status() -> bool:
    res = subprocess.run(["git", "status"], capture_output=True)
    return b"working tree clean" in res.stdout


def on_branch(branch: str) -> bool:
    res = subprocess.run(["git", "branch"], capture_output=True)
    return b"* " + branch.encode("utf-8") in res.stdout


def tests_pass() -> bool:
    res = subprocess.run(["pytest"], capture_output=True)
    return res.returncode == 0


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
