import os
import json
import pathlib
import requests
import http.server
import urllib.parse
import typing as t

from gsc import cli


TIMEOUT_S = 30 * 60
LOCAL_PORT = 4004
HOME = str(pathlib.Path.home())
GSC_DIR = HOME + "/.gitscientist/"
GSC_TOKEN = GSC_DIR + ".gsc_token"

if os.getenv("GSC_ENV") == "dev":
    BASE_URL = "http://localhost:4000"
else:
    BASE_URL = "https://www.gitscientist.com"
API_URL = BASE_URL + "/api"


class NoUserError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class TokenHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)

        res = requests.get(API_URL + parsed_path.path)

        self.send_response(302)

        if not os.path.exists(GSC_DIR):
            os.makedirs(GSC_DIR)

        if res.status_code == 200:
            session_unique_id = json.loads(res.text)["session_unique_id"]

            with open(GSC_TOKEN, "w") as f:
                f.write(session_unique_id)

            self.send_header("Location", BASE_URL + "/login-success")
        else:
            try:
                os.remove(GSC_TOKEN)
            except OSError:
                pass

            self.send_header("Location", BASE_URL + "/login-failure")

        self.end_headers()

    def log_message(self, format, *args):
        return


def login(email: str):
    res = requests.post(API_URL + "/login", data={"email": email})

    if res.status_code != 200:
        raise AuthenticationError("User not found.")

    cli.info("We sent you an email. Click the link inside to login.")

    # Start a localhost HTTP server to wait for the email verification token.
    server = http.server.HTTPServer(("", LOCAL_PORT), TokenHandler)
    server.handle_request()

    # Check for new token to see if we logged in successfully
    try:
        get_token()
    except AuthenticationError:
        raise AuthenticationError("Login Failed.")


def get_token() -> str:
    try:
        return pathlib.Path(GSC_TOKEN).read_text()
    except FileNotFoundError:
        raise AuthenticationError("Not logged in.")


def cookies() -> t.Dict[str, str]:
    token = get_token()
    return dict(session_unique_id=token)
