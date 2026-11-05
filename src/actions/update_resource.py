from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, OutputField, PermissiveActionOutput
from soar_sdk.exceptions import ActionFailure
from soar_sdk.params import Param, Params

from ..asset import Asset
from ..client import CritsClient, CritsClientError, parse_json_object
from ._validators import ValidationError, validate_resource, validate_resource_id
from ._results import failed_client_result


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
        patch = parse_json_object(params.patch_data, "patch_data")
        client = CritsClient(asset.url, asset.username, asset.api_key, asset.verify_server_cert, asset.timeout)
        try:
            response = client.request(f"/api/v1/{resource}/{resource_id}/", method="patch", json_data=patch)
        finally:
            client.close()
    except CritsClientError as error:
        if error.has_response_data:
            return failed_client_result(error)  # type: ignore[return-value]
        raise ActionFailure(str(error)) from error
    except ValidationError as error:
        raise ActionFailure(str(error)) from error
    message = response.get("message", "") if isinstance(response, dict) else ""
    if asset.api_key:
        message = str(message).replace(asset.api_key, "<api_key>")
    if "success" not in str(message).lower():
        raise ActionFailure(f"Unable to update resource: {message}")
    soar.set_summary(UpdateResourceSummary(resource_id=resource_id))
    soar.set_message("Successfully updated resource")
    return [UpdateResourceOutput.model_validate(response)]


class UpdateResourceSummary(ActionOutput):
    resource_id: str
