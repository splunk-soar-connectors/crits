from typing import Any

import httpx
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, ActionResult, OutputField, PermissiveActionOutput
from soar_sdk.auth import StaticTokenAuth
from soar_sdk.exceptions import ActionFailure
from soar_sdk.params import Param, Params

from ..asset import Asset
from .utils import parse_json_object, redact, redact_data, validate_resource, validate_timeout


class CreateResourceParams(Params):
    resource: str = Param(description="New Resource Type", primary=True, value_list=["actors", "actoridentifiers", "backdoors", "campaigns", "certificates", "domains", "emails", "events", "exploits", "indicators", "ips", "pcaps", "raw_data", "samples", "screenshots", "targets"], cef_types=["crits resource"])
    vault_id: str | None = Param(description="File to add to resource", primary=True, cef_types=["vault id"])
    source: str = Param(description="The Source of the resource")
    confidence: str | None = Param(description="Confidence", value_list=["low", "medium", "high"])
    post_data: str | None = Param(description="Post JSON Data")


class CreateResourceOutput(PermissiveActionOutput):
    id: str | None = OutputField(cef_types=["crits resource id"])
    message: str | None = None
    return_code: float | None = None
    type: str | None = OutputField(cef_types=["crits resource"])
    url: str | None = None


def _get_vault_file(soar: SOARClient, vault_id: str) -> tuple[str, Any]:
    try:
        attachments = soar.vault.get_attachment(vault_id=vault_id)
        attachment = next(iter(attachments))
    except StopIteration as error:
        raise ValueError("Vault file could not be found with supplied Vault ID") from error
    except Exception as error:
        raise ValueError("Vault ID not valid") from error
    if not attachment.path:
        raise ValueError("Could not find a path associated with the provided vault ID")
    try:
        return attachment.name, attachment.open("rb")
    except Exception as error:
        raise ValueError(f"Error reading file: {error}") from error


def create_resource(params: CreateResourceParams, soar: SOARClient, asset: Asset) -> list[CreateResourceOutput]:
    try:
        resource = validate_resource(params.resource)
    except ValueError as error:
        raise ActionFailure(str(error)) from error
    try:
        extra_data = parse_json_object(params.post_data, "post_data") if params.post_data else {}
    except ValueError as error:
        raise ActionFailure(redact(str(error), asset.api_key)) from error

    try:
        timeout = validate_timeout(asset.timeout)
    except ValueError as error:
        raise ActionFailure(str(error)) from error

    data: dict[str, Any] = {
        "source": params.source,
        "confidence": "low" if params.confidence is None else params.confidence,
    }
    upload = None
    file_data = None
    if params.vault_id:
        try:
            file_name, file_data = _get_vault_file(soar, params.vault_id)
        except ValueError as error:
            raise ActionFailure(str(error)) from error
        upload = {"filedata": (file_name, file_data)}
        data.update({"upload_type": "file", "file_format": "raw"})
    data.update(extra_data)

    auth = StaticTokenAuth(f"{asset.username}:{asset.api_key}", token_type="ApiKey")
    client = None
    try:
        client = httpx.Client(
            auth=auth,
            verify=asset.verify_server_cert,
            timeout=timeout,
            follow_redirects=True,
        )
        response = client.post(
            f"{asset.url.rstrip('/')}/api/v1/{resource}/",
            data=data,
            files=upload,
        )
    except httpx.HTTPError as error:
        raise ActionFailure(f"Error connecting: {redact(str(error), asset.api_key)}") from error
    finally:
        if client is not None:
            client.close()
        if file_data is not None:
            file_data.close()

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

    resource_id = response_data.get("id") if isinstance(response_data, dict) else None
    if not resource_id:
        message = response_data.get("message", "") if isinstance(response_data, dict) else ""
        message = redact(str(message), asset.api_key)
        raise ActionFailure(f"Unable to create resource: {message}")
    soar.set_summary(CreateResourceSummary(resource_id=str(resource_id)))
    soar.set_message("Successfully created new resource")
    return [CreateResourceOutput.model_validate(response_data)]


class CreateResourceSummary(ActionOutput):
    resource_id: str
