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
from soar_sdk.exceptions import ActionFailure

from ..asset import Asset
from ..auth import get_auth_client
from ..validators import validate_timeout
from .crits_client_utils import parse_connectivity_response, redact


def run_test_connectivity(soar: SOARClient, asset: Asset) -> None:
    try:
        timeout = validate_timeout(asset.timeout)
    except ValueError as error:
        raise ActionFailure(str(error)) from error
    api_key = asset.api_key
    client = get_auth_client(asset.username, api_key, asset.verify_server_cert, timeout)
    try:
        response = client.get(f"{asset.url.rstrip('/')}/api/v1/indicators/")
    except httpx.HTTPError as error:
        raise ActionFailure(
            f"Error connecting: {redact(str(error), api_key)}; Test connectivity failed"
        ) from error
    finally:
        client.close()
    parse_connectivity_response(response, api_key)
    soar.set_message("Test connectivity passed")
