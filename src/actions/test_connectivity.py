import httpx
from soar_sdk.abstract import SOARClient
from soar_sdk.exceptions import ActionFailure

from ..asset import Asset
from ..auth import get_auth_client
from ..validators import validate_timeout
from .crits_client_utils import parse_connectivity_response, redact


def run_test_connectivity(soar: SOARClient, asset: Asset) -> None:
    try:
        timeout = validate_timeout(asset.timeout)
    except ValueError as error:
        raise ActionFailure(str(error)) from error
    api_key = asset.api_key
    client = get_auth_client(asset.username, api_key, asset.verify_server_cert, timeout)
    try:
        response = client.get(f"{asset.url.rstrip('/')}/api/v1/indicators/")
    except httpx.HTTPError as error:
        raise ActionFailure(
            f"Error connecting: {redact(str(error), api_key)}; Test connectivity failed"
        ) from error
    finally:
        client.close()
    parse_connectivity_response(response, api_key)
    soar.set_message("Test connectivity passed")
