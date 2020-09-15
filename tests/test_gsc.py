from gsc import __version__
from typer.testing import CliRunner
from gsc.cli import app

runner = CliRunner()


def test_version():
    assert __version__ == "2.0.3"


def test_version_option():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_version_command():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout
