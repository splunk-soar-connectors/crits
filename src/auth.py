import httpx
from soar_sdk.auth import StaticTokenAuth


def get_auth_client(
    username: str,
    api_key: str,
    verify_server_cert: bool,
    timeout: int,
) -> httpx.Client:
    auth = StaticTokenAuth(f"{username}:{api_key}", token_type="ApiKey")
    return httpx.Client(
        auth=auth,
        verify=verify_server_cert,
        timeout=timeout,
        follow_redirects=True,
    )
