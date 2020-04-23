import os
import requests
from gsc import auth


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


def complete_exercise(id: str) -> str:
    cookies = auth.cookies()
    res = requests.get(API_URL + "/complete-exercise/" + id, cookies=cookies)
    if res.status_code == 200:
        return res.text
    raise api_error(res.status_code)


def api_error(sc: int) -> APIError:
    if sc == 403:
        return APIError("Please log in.")
    elif sc == 404:
        return APIError("Not found.")
    elif sc == 500:
        return APIError("Server error.")
    return APIError(f"Request failed with code {sc}")
