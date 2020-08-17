import os
import json
import requests
import typing as t

from gsc import auth, cli, verifier


if os.getenv("GSC_ENV") == "dev":
    API_URL = "http://localhost:4000/api"
else:
    API_URL = "https://www.gitscientist.com/api"


class APIError(Exception):
    pass


def ping() -> str:
    cookies = auth.cookies()
    res = requests.get(API_URL + "/ping", cookies=cookies)
    if res.status_code == 200:
        return res.text
    raise api_error(res.status_code)


def verify(id: str, payload: t.Dict[str, str]) -> str:
    cookies = auth.cookies()
    res = requests.post(API_URL + "/verify/" + id, json=payload, cookies=cookies)
    if res.status_code == 200:
        reply = json.loads(res.text)
        if reply["status"] == "ok":
            handle_warnings(reply)
            cli.success("Looks good.")
            return "Exercise complete"
        elif reply["status"] == "failed_verification":
            raise verifier.VerifyError(reply["msg"])
        elif reply["status"] == "error":
            raise APIError(reply["msg"])
        else:
            raise APIError("Unexpected API response. Try updating gsc.")
    raise api_error(res.status_code)


def handle_warnings(reply: t.Dict[str, t.Union[str, t.List[str]]]) -> None:
    list(map(cli.warn, reply["warnings"]))


def api_error(sc: int) -> APIError:
    if sc == 403:
        return APIError("Please log in.")
    elif sc == 404:
        return APIError("Not found.")
    elif sc == 500:
        return APIError("Server error.")
    elif sc == 400:
        return APIError("Please update gsc.\nUse `pip install --force gsc`.")
    return APIError(f"Request failed with code {sc}")
