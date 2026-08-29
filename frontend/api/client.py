"""
Minimal HTTP client used by every module in `api/`.

Keeps requests/error handling in one place so the resource-specific
modules (moradores, clientes, pagamentos, ...) only have to describe
*which* endpoint they call and with *which* parameters.
"""

from typing import Any, Optional

import requests

from config import settings


class ApiError(Exception):
    """Raised whenever a call to the backend fails or returns an error."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def _request(method: str, path: str, params: Optional[dict] = None) -> Any:
    url = f"{settings.API_BASE_URL}{path}"

    # Drop empty/None params so the backend sees only what's meaningful,
    # since most endpoints treat these as plain query parameters.
    clean_params = {k: v for k, v in (params or {}).items() if v is not None}

    try:
        response = requests.request(
            method, url, params=clean_params, timeout=settings.REQUEST_TIMEOUT
        )
    except requests.exceptions.ConnectionError as exc:
        raise ApiError(
            f"Não foi possível conectar à API em {settings.API_BASE_URL}."
        ) from exc
    except requests.exceptions.Timeout as exc:
        raise ApiError("A requisição à API expirou (timeout).") from exc
    except requests.exceptions.RequestException as exc:
        raise ApiError(f"Falha ao chamar a API: {exc}") from exc

    if response.status_code >= 400:
        detail = response.text
        try:
            payload = response.json()
            detail = payload.get("detail", detail)
        except ValueError:
            pass
        raise ApiError(f"Erro {response.status_code}: {detail}", response.status_code)

    if response.status_code == 204 or not response.content:
        return None

    try:
        return response.json()
    except ValueError:
        return response.text


def get(path: str, params: Optional[dict] = None) -> Any:
    return _request("GET", path, params)


def post(path: str, params: Optional[dict] = None) -> Any:
    return _request("POST", path, params)


def put(path: str, params: Optional[dict] = None) -> Any:
    return _request("PUT", path, params)


def delete(path: str, params: Optional[dict] = None) -> Any:
    return _request("DELETE", path, params)
