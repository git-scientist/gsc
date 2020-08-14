from gsc import client
from gsc.exercises import utils


def verify():
    payload = {"git remote -v": utils.git_remote()}

    client.verify("ssh_clone", payload)
