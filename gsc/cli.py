import typer
import gsc
from gsc import auth, client, verifier, setup_exercise, reset_exercise

app = typer.Typer()


def success(msg: str):
    typer.secho(msg, fg=typer.colors.GREEN, bold=True)


def info(msg: str):
    typer.echo(msg)


def title(msg: str):
    typer.secho(msg + "\n", fg=typer.colors.GREEN, bold=True)


def warn(msg: str):
    typer.secho(msg + "\n", fg=typer.colors.YELLOW, bold=False)


def error(msg: str):
    typer.secho(msg, fg=typer.colors.RED, bold=True)
    raise typer.Exit(1)


@app.command()
def login(email: str = typer.Option(..., prompt=True)):
    try:
        auth.login(email)
        success("Login Success.")
    except auth.LoginError as e:
        error(str(e))


@app.command()
def ping():
    try:
        client.ping()
        success("Pong.")
    except auth.AuthenticationError as e:
        error(str(e))
    except client.APIError as e:
        error(str(e))


@app.command()
def setup(exercise: str = typer.Argument(None)):
    try:
        setup_exercise.setup(exercise)
        success("Done.")
    except setup_exercise.SetupError as e:
        error(str(e))


@app.command()
def reset():
    try:
        reset_exercise.reset()
        success("Exercise reset.")
    except setup_exercise.SetupError as e:
        error(str(e))
    except reset_exercise.ResetError as e:
        error(str(e))


@app.command()
def verify(exercise: str = typer.Argument(None)):
    try:
        verifier.verify(exercise)
        success("Exercise complete!")
    except verifier.VerifyError as e:
        error(str(e))
    except auth.AuthenticationError as e:
        error(str(e))
    except client.APIError as e:
        error(str(e))


@app.callback()
def version_callback(value: bool):
    if value:
        version()


@app.command(hidden=True)
def version():
    typer.echo(f"gsc version: {gsc.__version__}")
    raise typer.Exit()


@app.callback()
def options(version: bool = typer.Option(None, "--version", callback=version_callback)):
    """
    gsc is the Git for Scientists practical exercise helper.

    See https://www.gitscientist.com for more.
    """


def main():
    app()
