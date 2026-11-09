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
from pydantic import model_validator
from soar_sdk.action_results import (
    ActionOutput,
    ActionResult,
    OutputField,
    PermissiveActionOutput,
)
from soar_sdk.params import Param, Params
from soar_sdk.abstract import SOARClient
from soar_sdk.exceptions import ActionFailure

from ..asset import Asset
from ..auth import get_auth_client
from ..validators import (
    parse_json_object,
    validate_integer,
    validate_next_page,
    validate_resource,
    validate_timeout,
)
from .crits_client_utils import parse_crits_response, redact


class RunQueryParams(Params):
    resource: str | None = Param(
        description="Resource to query on. Required if no Page URI is present",
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
    query: str | None = Param(
        description="Query to run", primary=True, cef_types=["crits query"]
    )
    limit: float | None = Param(description="Results per page")
    offset: float | None = Param(description="Paging offset")
    next_page: str | None = Param(description="Next page URI")


class _CRITsOutput(PermissiveActionOutput):
    @model_validator(mode="before")
    @classmethod
    def _wrap_scalar_record(cls, value: object) -> object:
        return value if isinstance(value, dict) else {"value": value}


class _ActivityOutput(_CRITsOutput):
    analyst: str | None = None
    date: str | None = None
    description: str | None = None
    end_date: str | None = None
    start_date: str | None = None


class _CampaignOutput(_CRITsOutput):
    analyst: str | None = None
    confidence: str | None = None
    date: str | None = None
    description: str | None = None
    name: str | None = None


class _ConfidenceOutput(_CRITsOutput):
    analyst: str | None = None
    rating: str | None = None


class _ImpactOutput(_CRITsOutput):
    analyst: str | None = None
    rating: str | None = None


class _RelationshipsOutput(_CRITsOutput):
    analyst: str | None = None
    date: str | None = None
    rel_confidence: str | None = None
    rel_reason: str | None = None
    relationship: str | None = None
    relationship_date: str | None = None
    type: str | None = None
    value: str | None = None


class _InstancesOutput(_CRITsOutput):
    analyst: str | None = None
    date: str | None = None
    method: str | None = None
    reference: str | None = None


class _SourceOutput(_CRITsOutput):
    instances: list[_InstancesOutput] | None = None
    name: str | None = None


class RunQueryOutput(_CRITsOutput):
    id: str | None = OutputField(cef_types=["crits resource id"], alias="_id")
    activity: list[_ActivityOutput] | None = None
    attack_types: str | None = None
    campaign: list[_CampaignOutput] | None = None
    confidence: _ConfidenceOutput | None = None
    created: str | None = None
    description: str | None = None
    impact: _ImpactOutput | None = None
    lower: str | None = None
    modified: str | None = None
    relationships: list[_RelationshipsOutput] | None = None
    schema_version: float | None = None
    source: list[_SourceOutput] | None = None
    status: str | None = None
    threat_types: str | None = None
    type: str | None = OutputField(cef_types=["crits resource"])
    value: str | None = None
    domain: str | None = None
    analyst: str | None = None
    watchlistEnabled: bool | None = None


class RunQuerySummary(ActionOutput):
    total_results: int = 0
    next_page: str | None = None


def _set_query_summary(response_data: dict, api_key: str, soar: SOARClient) -> None:
    meta = response_data.get("meta") or {}
    next_page = meta.get("next") if isinstance(meta, dict) else None
    if next_page and api_key:
        next_page = str(next_page).replace(api_key, "<api_key>")
    total_results = meta.get("total_count", 0) if isinstance(meta, dict) else 0
    message = f"Total results: {total_results}"
    if next_page:
        message += f", Next page: {next_page}"
    soar.set_summary(RunQuerySummary(total_results=total_results, next_page=next_page))
    soar.set_message(message)


def run_query(
    params: RunQueryParams, soar: SOARClient, asset: Asset
) -> list[RunQueryOutput]:
    try:
        if params.next_page:
            endpoint = validate_next_page(params.next_page)
            query = None
        else:
            if not params.resource:
                raise ValueError("Parameter 'resource' is required")
            resource = validate_resource(params.resource)
            query = parse_json_object(params.query, "query") if params.query else {}
            query["offset"] = validate_integer(
                params.offset, "'offset' action parameter", allow_zero=True
            )
            query["limit"] = validate_integer(params.limit, "'limit' action parameter")
            endpoint = f"/api/v1/{resource}/"
    except ValueError as error:
        raise ActionFailure(str(error)) from error

    try:
        timeout = validate_timeout(asset.timeout)
    except ValueError as error:
        raise ActionFailure(str(error)) from error

    api_key = asset.api_key
    client = get_auth_client(asset.username, api_key, asset.verify_server_cert, timeout)
    try:
        request_url = f"{asset.url.rstrip('/')}/{endpoint.lstrip('/')}"
        if params.next_page:
            # The validated next-page URI already contains its paging query.
            response = client.get(request_url)
        else:
            response = client.get(
                request_url,
                params={
                    key: value
                    for key, value in (query or {}).items()
                    if value is not None
                },
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
        {
            "resource": params.resource,
            "query": params.query,
            "limit": params.limit,
            "offset": params.offset,
            "next_page": params.next_page,
        },
    )
    if isinstance(response_data, ActionResult):
        return response_data  # type: ignore[return-value]

    if not isinstance(response_data, dict):
        raise ActionFailure("CRITs query response was not a JSON object")
    _set_query_summary(response_data, api_key, soar)
    objects = response_data.get("objects") or []
    return [
        RunQueryOutput.model_validate(
            item if isinstance(item, dict) else {"value": item}
        )
        for item in objects
    ]
