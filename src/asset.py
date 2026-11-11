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

from soar_sdk.asset import AssetField, BaseAsset, FieldCategory


class Asset(BaseAsset):
    url: str = AssetField(
        description="Device URL e.g. https://mycrits.contoso.com:8080",
        category=FieldCategory.CONNECTIVITY,
    )
    verify_server_cert: bool = AssetField(
        description="Verify server certificate",
        default=True,
        required=False,
        category=FieldCategory.CONNECTIVITY,
    )
    username: str = AssetField(
        description="Username", category=FieldCategory.CONNECTIVITY
    )
    api_key: str = AssetField(
        description="API Key", sensitive=True, category=FieldCategory.CONNECTIVITY
    )
    timeout: float = AssetField(
        description="Request Timeout (Default: 30 seconds)",
        default=30.0,
        required=False,
        category=FieldCategory.CONNECTIVITY,
    )
