import os
import json
import pathlib
import asyncio
import websockets
import typing as t

from gsc import cli


TIMEOUT_S = 30 * 60
LOCAL_PORT = 4004
HOME = str(pathlib.Path.home())
GSC_DIR = HOME + "/.gitscientist/"
GSC_TOKEN = GSC_DIR + ".gsc_token"

if os.getenv("GSC_ENV") == "dev":
    BASE_URL = "ws://localhost:4000"
else:
    BASE_URL = "wss://www.gitscientist.com"


class LoginError(Exception):
    pass


class AuthenticationError(Exception):
    pass


async def handle_login(email: str):
    url = BASE_URL + "/socket/websocket"
    async with websockets.connect(url) as websocket:
        login_msg = {
            "topic": "login",
            "event": "phx_join",
            "payload": {"email": email},
            "ref": "",
        }
        await websocket.send(json.dumps(login_msg))

        while True:
            raw = await websocket.recv()
            resp = json.loads(raw)
            event = resp["event"]
            if event == "phx_reply":
                if resp["payload"]["status"] == "ok":
                    cli.info("We sent you an email. Click the link inside to log in.")
                else:
                    raise LoginError(
                        "Login failed unexpectedly.\n"
                        f'Response: {json.dumps(resp["payload"]["response"])}\n'
                        "Contact us if this error persists."
                    )
                    break

            elif event == "login_success":
                session_unique_id = resp["payload"]["session_unique_id"]

                if not os.path.exists(GSC_DIR):
                    os.makedirs(GSC_DIR)

                with open(GSC_TOKEN, "w") as f:
                    f.write(session_unique_id)
                break

            elif event == "error":
                raise LoginError(
                    f'Login failed.\nReason: {resp["payload"]["reason"]}\n'
                )
                break


def login(email: str):
    asyncio.get_event_loop().run_until_complete(handle_login(email))


def get_token() -> str:
    try:
        return pathlib.Path(GSC_TOKEN).read_text()
    except FileNotFoundError:
        raise AuthenticationError("Not logged in.")


def cookies() -> t.Dict[str, str]:
    token = get_token()
    return dict(session_unique_id=token)
