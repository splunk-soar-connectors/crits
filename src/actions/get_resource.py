from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import PermissiveActionOutput, OutputField
from soar_sdk.exceptions import ActionFailure
from soar_sdk.params import Param, Params

from ..asset import Asset
from ..client import CritsClient, CritsClientError
from ._validators import ValidationError, validate_resource, validate_resource_id
from ._results import failed_client_result


class GetResourceParams(Params):
    id: str = Param(description="Resource ID to get", primary=True, cef_types=["crits resource id"])
    resource: str = Param(description="Resource to get", primary=True, value_list=["actors", "actoridentifiers", "backdoors", "campaigns", "certificates", "domains", "emails", "events", "exploits", "indicators", "ips", "pcaps", "raw_data", "samples", "screenshots", "targets"], cef_types=["crits resource"])


class _ActivityOutput(PermissiveActionOutput):
    analyst: str | None = None
    date: str | None = None
    description: str | None = None
    end_date: str | None = None
    start_date: str | None = None


class _CampaignOutput(PermissiveActionOutput):
    analyst: str | None = None
    confidence: str | None = None
    date: str | None = None
    description: str | None = None
    name: str | None = None


class _ConfidenceOutput(PermissiveActionOutput):
    analyst: str | None = None
    rating: str | None = None


class _ImpactOutput(PermissiveActionOutput):
    analyst: str | None = None
    rating: str | None = None


class _RelationshipsOutput(PermissiveActionOutput):
    analyst: str | None = None
    date: str | None = None
    rel_confidence: str | None = None
    rel_reason: str | None = None
    relationship: str | None = None
    relationship_date: str | None = None
    type: str | None = None
    value: str | None = None


class _InstancesOutput(PermissiveActionOutput):
    analyst: str | None = None
    date: str | None = None
    method: str | None = None
    reference: str | None = None


class _SourceOutput(PermissiveActionOutput):
    instances: list[_InstancesOutput] | None = None
    name: str | None = None


class GetResourceOutput(PermissiveActionOutput):
    id: str | None = OutputField(cef_types=["crits resource id"], alias="_id")
    created: str | None = None
    activity: list[_ActivityOutput] | None = None
    attack_types: str | None = None
    campaign: list[_CampaignOutput] | None = None
    confidence: _ConfidenceOutput | None = None
    description: str | None = None
    filedata: str | None = None
    filename: str | None = None
    filetype: str | None = None
    impact: _ImpactOutput | None = None
    lower: str | None = None
    md5: str | None = None
    mimetype: str | None = None
    modified: str | None = None
    name: str | None = None
    relationships: list[_RelationshipsOutput] | None = None
    schema_version: float | None = None
    sha1: str | None = None
    sha256: str | None = None
    size: float | None = None
    source: list[_SourceOutput] | None = None
    ssdeep: str | None = None
    status: str | None = None
    threat_types: str | None = None
    type: str | None = None
    value: str | None = None


def get_resource(params: GetResourceParams, soar: SOARClient, asset: Asset) -> list[GetResourceOutput]:
    try:
        resource = validate_resource(params.resource)
        resource_id = validate_resource_id(params.id)
        client = CritsClient(asset.url, asset.username, asset.api_key, asset.verify_server_cert, asset.timeout)
        try:
            response = client.request(f"/api/v1/{resource}/{resource_id}/")
        finally:
            client.close()
    except CritsClientError as error:
        if error.has_response_data:
            return failed_client_result(error)  # type: ignore[return-value]
        raise ActionFailure(str(error)) from error
    except ValidationError as error:
        raise ActionFailure(str(error)) from error
    if not isinstance(response, dict):
        raise ActionFailure("CRITs resource response was not a JSON object")
    soar.set_message("Successfully retrieved resource")
    return [GetResourceOutput.model_validate(response)]
