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

from typing import Any

import httpx
from soar_sdk.action_results import ActionResult
from soar_sdk.exceptions import ActionFailure


def redact(value: str, secret: str) -> str:
    return value.replace(secret, "<api_key>") if secret else value


def redact_data(value: Any, secret: str) -> Any:
    if isinstance(value, str):
        return redact(value, secret)
    if isinstance(value, list):
        return [redact_data(item, secret) for item in value]
    if isinstance(value, dict):
        return {
            redact(key, secret): redact_data(item, secret)
            for key, item in value.items()
        }
    return value


def parse_crits_response(
    response: httpx.Response,
    api_key: str,
    action_parameters: dict[str, Any],
) -> Any:
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as error:
        response = error.response
        content_type = response.headers.get("Content-Type", "")
        if "json" not in content_type:
            message = "Can't process response from server. Status Code: {} Data from server: {}".format(
                response.status_code,
                response.text.replace("{", "{{").replace("}", "}}"),
            )
            raise ActionFailure(redact(message, api_key)) from error
        try:
            response_data = response.json()
        except ValueError as parse_error:
            raise ActionFailure(
                f"Unable to parse response as JSON: {redact(str(parse_error), api_key)}"
            ) from parse_error
        message = (
            response_data.get("error_message")
            if isinstance(response_data, dict)
            else None
        )
        if not message:
            message = response.text.replace("{", "{{").replace("}", "}}")
        result = ActionResult(
            status=False,
            message=redact(
                f"Error from server, Status Code: {response.status_code} data returned: {message}",
                api_key,
            ),
            param=redact_data(action_parameters, api_key),
        )
        result.add_data(redact_data(response_data, api_key))
        return result

    if "json" not in response.headers.get("Content-Type", ""):
        if 200 <= response.status_code < 205 and not response.text:
            raise ActionFailure("The server returned an empty response")
        message = "Can't process response from server. Status Code: {} Data from server: {}".format(
            response.status_code, response.text.replace("{", "{{").replace("}", "}}")
        )
        raise ActionFailure(redact(message, api_key))
    try:
        response_data = response.json()
    except ValueError as error:
        raise ActionFailure(
            f"Unable to parse response as JSON: {redact(str(error), api_key)}"
        ) from error
    if response.status_code == 205:
        message = (
            response_data.get("error_message")
            if isinstance(response_data, dict)
            else None
        )
        if not message:
            message = response.text.replace("{", "{{").replace("}", "}}")
        result = ActionResult(
            status=False,
            message=redact(
                f"Error from server, Status Code: {response.status_code} data returned: {message}",
                api_key,
            ),
            param=redact_data(action_parameters, api_key),
        )
        result.add_data(redact_data(response_data, api_key))
        return result
    return response_data


def parse_connectivity_response(response: httpx.Response, api_key: str) -> None:
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as error:
        response = error.response
        message = f"HTTP {response.status_code}"
        if "json" in response.headers.get("Content-Type", ""):
            try:
                response_data = response.json()
            except ValueError as parse_error:
                raise ActionFailure(
                    f"Test connectivity failed: unable to parse error response: {redact(str(parse_error), api_key)}"
                ) from error
            if isinstance(response_data, dict):
                message = str(response_data.get("error_message") or message)
        raise ActionFailure(
            f"{redact(message, api_key)}; Test connectivity failed"
        ) from error

    if "json" not in response.headers.get("Content-Type", ""):
        raise ActionFailure(
            f"Test connectivity failed: server returned HTTP {response.status_code} with a non-JSON response"
        )
    try:
        response_data = response.json()
    except ValueError as error:
        raise ActionFailure(
            f"Test connectivity failed: unable to parse JSON response: {redact(str(error), api_key)}"
        ) from error
    if not isinstance(response_data, dict):
        raise ActionFailure("Test connectivity failed: unexpected response")
