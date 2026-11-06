import httpx
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, ActionResult, OutputField, PermissiveActionOutput
from soar_sdk.auth import StaticTokenAuth
from soar_sdk.exceptions import ActionFailure
from soar_sdk.params import Param, Params

from ..asset import Asset
from .utils import parse_json_object, redact, redact_data, validate_resource, validate_resource_id, validate_timeout


class UpdateResourceParams(Params):
    id: str = Param(description="Resource ID to update", primary=True, cef_types=["crits resource id"])
    resource: str = Param(description="Resource type to update", primary=True, value_list=["actors", "actoridentifiers", "backdoors", "campaigns", "certificates", "domains", "emails", "events", "exploits", "indicators", "ips", "pcaps", "raw_data", "samples", "screenshots", "targets"], cef_types=["crits resource"])
    patch_data: str = Param(description="Update JSON Data")


class UpdateResourceOutput(PermissiveActionOutput):
    id: str | None = OutputField(cef_types=["crits resource id"])
    message: str | None = None
    return_code: float | None = None
    type: str | None = OutputField(cef_types=["crits resource"])


def update_resource(params: UpdateResourceParams, soar: SOARClient, asset: Asset) -> list[UpdateResourceOutput]:
    try:
        resource = validate_resource(params.resource)
        resource_id = validate_resource_id(params.id)
    except ValueError as error:
        raise ActionFailure(str(error)) from error
    try:
        patch = parse_json_object(params.patch_data, "patch_data")
    except ValueError as error:
        raise ActionFailure(redact(str(error), asset.api_key)) from error

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
        response = client.patch(
            f"{asset.url.rstrip('/')}/api/v1/{resource}/{resource_id}/",
            json=patch,
        )
    except httpx.HTTPError as error:
        raise ActionFailure(f"Error connecting: {redact(str(error), asset.api_key)}") from error
    finally:
        client.close()

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as error:
        response = error.response
        content_type = response.headers.get("Content-Type", "")
        if "json" not in content_type:
            message = "Can't process response from server. Status Code: {} Data from server: {}".format(
                response.status_code, response.text.replace("{", "{{").replace("}", "}}")
            )
            raise ActionFailure(redact(message, asset.api_key)) from error
        try:
            response_data = response.json()
        except ValueError as parse_error:
            raise ActionFailure(
                f"Unable to parse response as JSON: {redact(str(parse_error), asset.api_key)}"
            ) from parse_error
        message = response_data.get("error_message") if isinstance(response_data, dict) else None
        if not message:
            message = response.text.replace("{", "{{").replace("}", "}}")
        result = ActionResult(
            status=False,
            message=redact(f"Error from server, Status Code: {response.status_code} data returned: {message}", asset.api_key),
        )
        result.add_data(redact_data(response_data, asset.api_key))
        return result  # type: ignore[return-value]

    if "json" not in response.headers.get("Content-Type", ""):
        if 200 <= response.status_code < 205 and not response.text:
            raise ActionFailure("The server returned an empty response")
        message = "Can't process response from server. Status Code: {} Data from server: {}".format(
            response.status_code, response.text.replace("{", "{{").replace("}", "}}")
        )
        raise ActionFailure(redact(message, asset.api_key))
    try:
        response_data = response.json()
    except ValueError as error:
        raise ActionFailure(f"Unable to parse response as JSON: {redact(str(error), asset.api_key)}") from error
    if response.status_code == 205:  # Preserve the legacy 200-204 success range.
        message = response_data.get("error_message") if isinstance(response_data, dict) else None
        if not message:
            message = response.text.replace("{", "{{").replace("}", "}}")
        result = ActionResult(
            status=False,
            message=redact(f"Error from server, Status Code: {response.status_code} data returned: {message}", asset.api_key),
        )
        result.add_data(redact_data(response_data, asset.api_key))
        return result  # type: ignore[return-value]

    message = response_data.get("message", "") if isinstance(response_data, dict) else ""
    message = redact(str(message), asset.api_key)
    if "success" not in str(message).lower():
        raise ActionFailure(f"Unable to update resource: {message}")
    soar.set_summary(UpdateResourceSummary(resource_id=resource_id))
    soar.set_message("Successfully updated resource")
    return [UpdateResourceOutput.model_validate(response_data)]


class UpdateResourceSummary(ActionOutput):
    resource_id: str
