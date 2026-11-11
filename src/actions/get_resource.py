# Copyright (c) 2026 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import httpx
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import (
    ActionOutput,
    ActionResult,
    PermissiveActionOutput,
    OutputField,
)
from soar_sdk.exceptions import ActionFailure
from soar_sdk.params import Param, Params

from ..asset import Asset
from ..auth import get_auth_client
from ..validators import validate_resource, validate_resource_id, validate_timeout
from .crits_client_utils import parse_crits_response, redact


class GetResourceParams(Params):
    id: str = Param(
        description="Resource ID to get", primary=True, cef_types=["crits resource id"]
    )
    resource: str = Param(
        description="Resource to get",
        primary=True,
        value_list=[
            "actors",
            "actoridentifiers",
            "backdoors",
            "campaigns",
            "certificates",
            "domains",
            "emails",
            "events",
            "exploits",
            "indicators",
            "ips",
            "pcaps",
            "raw_data",
            "samples",
            "screenshots",
            "targets",
        ],
        cef_types=["crits resource"],
    )


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


class GetResourceSummary(ActionOutput):
    resource_id: str = OutputField(cef_types=["crits resource id"])


def get_resource(
    params: GetResourceParams, soar: SOARClient, asset: Asset
) -> list[GetResourceOutput]:
    try:
        resource = validate_resource(params.resource)
        resource_id = validate_resource_id(params.id)
    except ValueError as error:
        raise ActionFailure(str(error)) from error
    try:
        timeout = validate_timeout(asset.timeout)
    except ValueError as error:
        raise ActionFailure(str(error)) from error

    api_key = asset.api_key
    client = get_auth_client(asset.username, api_key, asset.verify_server_cert, timeout)
    try:
        response = client.get(
            f"{asset.url.rstrip('/')}/api/v1/{resource}/{resource_id}/"
        )
    except httpx.HTTPError as error:
        raise ActionFailure(
            f"Error connecting: {redact(str(error), api_key)}"
        ) from error
    finally:
        client.close()
    response_data = parse_crits_response(
        response,
        api_key,
        {"id": params.id, "resource": params.resource},
    )
    if isinstance(response_data, ActionResult):
        return response_data  # type: ignore[return-value]
    if not isinstance(response_data, dict):
        raise ActionFailure("CRITs resource response was not a JSON object")
    soar.set_summary(GetResourceSummary(resource_id=resource_id))
    soar.set_message("Successfully retrieved resource")
    return [GetResourceOutput.model_validate(response_data)]
