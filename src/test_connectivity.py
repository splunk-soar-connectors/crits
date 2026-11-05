from soar_sdk.abstract import SOARClient
from soar_sdk.exceptions import ActionFailure

from src.asset import Asset
from src.client import CritsClient, CritsClientError


def run_test_connectivity(soar: SOARClient, asset: Asset) -> None:
    client: CritsClient | None = None
    try:
        client = CritsClient(asset.url, asset.username, asset.api_key, asset.verify_server_cert, asset.timeout)
        response = client.request("/api/v1/indicators/")
    except CritsClientError as error:
        raise ActionFailure(f"{error}; Test connectivity failed") from error
    finally:
        if client is not None:
            client.close()
    if not isinstance(response, dict):
        raise ActionFailure("Test connectivity failed: unexpected response")
    soar.set_message("Test connectivity passed")
