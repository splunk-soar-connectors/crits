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

import json
from typing import Any

import httpx
from soar_sdk.action_results import MakeRequestOutput
from soar_sdk.exceptions import ActionFailure
from soar_sdk.params import MakeRequestParams

from ..asset import Asset
from ..auth import get_auth_client
from ..validators import (
    parse_json_object,
    parse_query_parameters,
    validate_http_method,
    validate_request_endpoint,
    validate_timeout,
)
from .crits_client_utils import redact


def make_request(params: MakeRequestParams, asset: Asset) -> MakeRequestOutput:
    api_key = asset.api_key
    try:
        method = validate_http_method(params.http_method)
        endpoint = validate_request_endpoint(params.endpoint)
        headers = parse_json_object(params.headers, "headers") if params.headers else {}
        query_parameters = parse_query_parameters(params.query_parameters)
        timeout = validate_timeout(
            params.timeout if params.timeout is not None else asset.timeout
        )
    except ValueError as error:
        raise ActionFailure(redact(str(error), api_key)) from error

    if any(
        not isinstance(key, str) or not isinstance(value, str)
        for key, value in headers.items()
    ):
        raise ActionFailure(
            "Request headers must be a JSON object with string keys and values"
        )

    request_kwargs: dict[str, Any] = {}
    if params.body is not None:
        try:
            request_kwargs["json"] = json.loads(params.body)
        except ValueError:
            request_kwargs["content"] = params.body

    verify_ssl = (
        params.verify_ssl
        if "verify_ssl" in params.model_fields_set
        else asset.verify_server_cert
    )
    client = get_auth_client(asset.username, api_key, verify_ssl, timeout)
    try:
        response = client.request(
            method,
            f"{asset.url.rstrip('/')}/{endpoint.lstrip('/')}",
            params=query_parameters,
            headers=headers,
            **request_kwargs,
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            response = error.response
    except httpx.HTTPError as error:
        raise ActionFailure(
            f"Error connecting: {redact(str(error), api_key)}"
        ) from error
    finally:
        client.close()

    return MakeRequestOutput(
        status_code=response.status_code,
        response_body=redact(response.text, api_key),
    )
