import httpx
from soar_sdk.abstract import SOARClient
from soar_sdk.auth import StaticTokenAuth
from soar_sdk.exceptions import ActionFailure

from ..asset import Asset
from .utils import redact, validate_timeout


def run_test_connectivity(soar: SOARClient, asset: Asset) -> None:
    try:
        timeout = validate_timeout(asset.timeout)
    except ValueError as error:
        raise ActionFailure(str(error)) from error
    auth = StaticTokenAuth(f"{asset.username}:{asset.api_key}", token_type="ApiKey")
    client = httpx.Client(
        auth=auth,
        verify=asset.verify_server_cert,
        timeout=timeout,
        follow_redirects=True,
    )
    try:
        response = client.get(f"{asset.url.rstrip('/')}/api/v1/indicators/")
    except httpx.HTTPError as error:
        raise ActionFailure(f"Error connecting: {redact(str(error), asset.api_key)}; Test connectivity failed") from error
    finally:
        client.close()

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as error:
        response = error.response
        message = f"HTTP {response.status_code}"
        if "json" in response.headers.get("Content-Type", ""):
            try:
                response_data = response.json()
            except ValueError as parse_error:
                raise ActionFailure(
                    f"Test connectivity failed: unable to parse error response: {redact(str(parse_error), asset.api_key)}"
                ) from error
            if isinstance(response_data, dict):
                message = str(response_data.get("error_message") or message)
        raise ActionFailure(f"{redact(message, asset.api_key)}; Test connectivity failed") from error

    if "json" not in response.headers.get("Content-Type", ""):
        raise ActionFailure(f"Test connectivity failed: server returned HTTP {response.status_code} with a non-JSON response")
    try:
        response_data = response.json()
    except ValueError as error:
        raise ActionFailure(f"Test connectivity failed: unable to parse JSON response: {redact(str(error), asset.api_key)}") from error
    if not isinstance(response_data, dict):
        raise ActionFailure("Test connectivity failed: unexpected response")
    soar.set_message("Test connectivity passed")
