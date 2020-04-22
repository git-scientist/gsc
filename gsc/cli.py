import typer
from gsc import auth, client

app = typer.Typer()


@app.command("login")
def login(email: str = typer.Option(..., prompt=True)):
    try:
        auth.login(email)
        typer.secho("Login Success.", fg=typer.colors.GREEN, bold=True)
    except auth.AuthenticationError as e:
        typer.secho(str(e), fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)


@app.command("ping")
def ping():
    try:
        client.ping()
        typer.secho("Pong.", fg=typer.colors.GREEN, bold=True)
    except auth.AuthenticationError as e:
        typer.secho(str(e), fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)
    except client.APIError as e:
        typer.secho(str(e), fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)


def main():
    app()
