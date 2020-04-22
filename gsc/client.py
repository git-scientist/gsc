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


def api_error(sc: int) -> APIError:
    return APIError(f"Request failed with code {sc}")
