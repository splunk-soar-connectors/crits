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
    OutputField,
    PermissiveActionOutput,
)
from soar_sdk.exceptions import ActionFailure
from soar_sdk.params import Param, Params

from ..asset import Asset
from ..auth import get_auth_client
from ..validators import (
    parse_json_object,
    validate_resource,
    validate_resource_id,
    validate_timeout,
)
from .crits_client_utils import parse_crits_response, redact


class UpdateResourceParams(Params):
    id: str = Param(
        description="Resource ID to update",
        primary=True,
        cef_types=["crits resource id"],
    )
    resource: str = Param(
        description="Resource type to update",
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
    patch_data: str = Param(description="Update JSON Data")


class UpdateResourceOutput(PermissiveActionOutput):
    id: str | None = OutputField(cef_types=["crits resource id"])
    message: str | None = None
    return_code: float | None = None
    type: str | None = OutputField(cef_types=["crits resource"])


def update_resource(
    params: UpdateResourceParams, soar: SOARClient, asset: Asset
) -> list[UpdateResourceOutput]:
    api_key = asset.api_key
    try:
        resource = validate_resource(params.resource)
        resource_id = validate_resource_id(params.id)
    except ValueError as error:
        raise ActionFailure(str(error)) from error
    try:
        patch = parse_json_object(params.patch_data, "patch_data")
    except ValueError as error:
        raise ActionFailure(redact(str(error), api_key)) from error
    try:
        timeout = validate_timeout(asset.timeout)
    except ValueError as error:
        raise ActionFailure(str(error)) from error

    client = get_auth_client(asset.username, api_key, asset.verify_server_cert, timeout)
    try:
        response = client.patch(
            f"{asset.url.rstrip('/')}/api/v1/{resource}/{resource_id}/",
            json=patch,
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
        {"id": params.id, "resource": params.resource, "patch_data": params.patch_data},
    )
    if isinstance(response_data, ActionResult):
        return response_data  # type: ignore[return-value]
    message = (
        response_data.get("message", "") if isinstance(response_data, dict) else ""
    )
    message = redact(str(message), api_key)
    if not str(message).lower().startswith("success"):
        raise ActionFailure(f"Unable to update resource: {message}")
    soar.set_summary(UpdateResourceSummary(resource_id=resource_id))
    soar.set_message("Successfully updated resource")
    return [UpdateResourceOutput.model_validate(response_data)]


class UpdateResourceSummary(ActionOutput):
    resource_id: str
