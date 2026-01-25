import requests
from core.config import BACKEND_BASE_URL
import logging

logger = logging.getLogger(__name__)

class APIError(RuntimeError):
    pass

def _handle(resp: requests.Response):
    if resp.status_code >= 400:
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise APIError(f"API {resp.status_code}: {detail}")
    return resp.json() if resp.content else {}

def get(path: str, params=None, headers=None):
    print(f"Making GET request to {BACKEND_BASE_URL}{path} with params {params}")
    logger.info(f"Making GET request to {BACKEND_BASE_URL}{path} with params {params}")
    url = f"{BACKEND_BASE_URL}{path}"
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        print(f"Received response: {resp.status_code} - {resp}")
        return _handle(resp)
    except requests.RequestException as e:
        logger.error(f"Request to {url} failed: {e}")
        raise APIError(f"Request to {url} failed: {e}")

def post(path: str, json=None, headers=None):
    url = f"{BACKEND_BASE_URL}{path}"
    resp = requests.post(url, json=json, headers=headers, timeout=20)
    return _handle(resp)
