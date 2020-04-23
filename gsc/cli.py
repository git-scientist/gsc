import typer
from gsc import auth, client, verifier

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


@app.command("login")
def login(email: str = typer.Option(..., prompt=True)):
    try:
        auth.login(email)
        success("🎉 Login Success.")
    except auth.AuthenticationError as e:
        error(str(e))


@app.command("ping")
def ping():
    try:
        client.ping()
        success("Pong.")
    except auth.AuthenticationError as e:
        error(str(e))
    except client.APIError as e:
        error(str(e))


@app.command("verify")
def verify():
    try:
        client.ping()
        verifier.verify()
        success("✔️  Exercise complete!")
    except verifier.VerifyError as e:
        error(str(e))
    except auth.AuthenticationError as e:
        error(str(e))
    except client.APIError as e:
        error(str(e))


def main():
    app()
