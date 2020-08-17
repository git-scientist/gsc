from gsc import cli, client
from gsc.exercises import utils


def setup():
    cli.info("There's no setup for this exercise.")


def reset():
    cli.info("There's no reset for this exercise.")


def verify():
    payload = {"git remote -v": utils.git_remote()}
    client.verify("multiple_remotes", payload)
