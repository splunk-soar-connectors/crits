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
from soar_sdk.auth import StaticTokenAuth


def get_auth_client(
    username: str,
    api_key: str,
    verify_server_cert: bool,
    timeout: int,
) -> httpx.Client:
    # ApiKey is the CRITs authentication scheme, not a credential value.
    auth = StaticTokenAuth(f"{username}:{api_key}", token_type="ApiKey")  # noqa: S106
    return httpx.Client(
        auth=auth,
        verify=verify_server_cert,
        timeout=timeout,
        follow_redirects=True,
    )
