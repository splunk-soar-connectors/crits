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
from soar_sdk.abstract import SOARClient
from soar_sdk.app import App
from soar_sdk.params import Param, Params
from soar_sdk.action_results import ActionOutput, OutputField
from soar_sdk.asset import BaseAsset, AssetField
from soar_sdk.logging import getLogger

logger = getLogger()


class Asset(BaseAsset):
    url: str = AssetField(
        description="Device URL e.g. https://mycrits.contoso.com:8080"
    )
    verify_server_cert: bool | None = AssetField(
        description="Verify server certificate", default=True
    )
    username: str = AssetField(description="Username")
    api_key: str = AssetField(description="API Key")
    timeout: float | None = AssetField(
        description="Request Timeout (Default: 30 seconds)", default=30.0
    )


app = App(
    name="crits",
    app_type="siem",
    logo="logo_crits.svg",
    logo_dark="logo_crits_dark.svg",
    product_vendor="MITRE",
    product_name="CRITs",
    publisher="Splunk",
    appid="ef9cfabb-f011-43c3-bc8b-0ef30a04bf35",
    fips_compliant=True,
    encrypt_cache_state=True,
    encrypt_ingest_state=True,
    asset_cls=Asset,
)


@app.test_connectivity()
def test_connectivity(soar: SOARClient, asset: Asset) -> None:
    raise NotImplementedError()


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


class ActivityOutput(ActionOutput):
    analyst: str = OutputField(example_values=["admin"])
    date: str = OutputField(example_values=["2017-06-23 17:46:36.544000"])
    description: str = OutputField(example_values=["Metal Claws"])
    end_date: str = OutputField(example_values=["2017-06-23 17:46:36.544000"])
    start_date: str = OutputField(example_values=["2017-06-23 17:46:36.544000"])


class CampaignOutput(ActionOutput):
    analyst: str
    confidence: str
    date: str
    description: str
    name: str


class ConfidenceOutput(ActionOutput):
    analyst: str
    rating: str


class ImpactOutput(ActionOutput):
    analyst: str
    rating: str


class RelationshipsOutput(ActionOutput):
    analyst: str
    date: str
    rel_confidence: str
    rel_reason: str
    relationship: str
    relationship_date: str
    type: str
    value: str


class InstancesOutput(ActionOutput):
    analyst: str
    date: str
    method: str
    reference: str


class SourceOutput(ActionOutput):
    instances: list[InstancesOutput]
    name: str


class RunQueryOutput(ActionOutput):
    id: str = OutputField(cef_types=["crits resource id"], alias="_id")
    activity: list[ActivityOutput]
    attack_types: str
    campaign: list[CampaignOutput]
    confidence: ConfidenceOutput
    created: str
    description: str
    impact: ImpactOutput
    lower: str
    modified: str
    relationships: list[RelationshipsOutput]
    schema_version: float
    source: list[SourceOutput]
    status: str
    threat_types: str
    type: str = OutputField(cef_types=["crits resource"])
    value: str
    domain: str = OutputField(example_values=["mobilalibey.com"])
    analyst: str = OutputField(example_values=["scott"])
    watchlistEnabled: bool


@app.action(
    description="Run a search query on the CRITs device",
    action_type="investigate",
    verbose='Query on CRITs is made up of multiple instances of key-value pairs, much like the parameters that are specified to an HTTP URL. To keep things simple, the action takes as input each parameter and its value to match as a JSON dictionary (in string form).<br>For example to search for an indicator of value <b>baddomain.com</b>:<ul><li>Set <b>resource</b> parameter to <b>indicators</b></li><li>The <b>query</b> parameter should be set to <b>{ \\"c-value\\": \\"baddomain.com\\" }</b></li></ul>To add more values to match just add the required key-value pairs to the <b>query</b> dictionary.<br>While orchestrating this action from the UI, typing the JSON dictionary should suffice.<br>While automating this action from a playbook, if you are creating a dictionary, then you will require to convert it into a JSON string using the json.loads(...) python function before passing it as the value to the <b>query</b> parameter.<br>If the next page URI is present, the other parameters will be ignored. If it isn\'t present, the resource to query on the field must be present.',
)
def run_query(params: RunQueryParams, soar: SOARClient, asset: Asset) -> RunQueryOutput:
    raise NotImplementedError()


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


class ActivityOutput(ActionOutput):
    analyst: str = OutputField(example_values=["admin"])
    date: str = OutputField(example_values=["2017-06-23 17:46:36.544000"])
    description: str = OutputField(example_values=["Metal Claws"])
    end_date: str = OutputField(example_values=["2017-06-23 17:46:36.544000"])
    start_date: str = OutputField(example_values=["2017-06-23 17:46:36.544000"])


class CampaignOutput(ActionOutput):
    analyst: str
    confidence: str
    date: str
    description: str
    name: str


class ConfidenceOutput(ActionOutput):
    analyst: str
    rating: str


class ImpactOutput(ActionOutput):
    analyst: str
    rating: str


class RelationshipsOutput(ActionOutput):
    analyst: str
    date: str
    rel_confidence: str
    rel_reason: str
    relationship: str
    relationship_date: str
    type: str
    value: str


class InstancesOutput(ActionOutput):
    analyst: str
    date: str
    method: str
    reference: str


class SourceOutput(ActionOutput):
    instances: list[InstancesOutput]
    name: str


class GetResourceOutput(ActionOutput):
    id: str = OutputField(cef_types=["crits resource id"], alias="_id")
    created: str
    activity: list[ActivityOutput]
    attack_types: str
    campaign: list[CampaignOutput]
    confidence: ConfidenceOutput
    description: str
    filedata: str = OutputField(example_values=["c2FtcGxlIGZpbGUgbGluZTE="])
    filename: str = OutputField(example_values=["ph_vault_datafile"])
    filetype: str = OutputField(example_values=["ASCII text, with no line terminators"])
    impact: ImpactOutput
    lower: str
    md5: str = OutputField(example_values=["testtestcdf080d433600809testtest"])
    mimetype: str = OutputField(example_values=["text/plain"])
    modified: str
    name: str = OutputField(example_values=["this is me"])
    relationships: list[RelationshipsOutput]
    schema_version: float
    sha1: str = OutputField(example_values=["testteste42e3d5a76a746e07aed942ctesttest"])
    sha256: str = OutputField(
        example_values=[
            "testtestb577f55b302b4485decb454ecf5748c286c745537317ff2etesttest"
        ]
    )
    size: float = OutputField(example_values=[17])
    source: list[SourceOutput]
    ssdeep: str = OutputField(example_values=["3:MRx:8x"])
    status: str
    threat_types: str
    type: str
    value: str


@app.action(description="Get a specific resource from CRITs", action_type="investigate")
def get_resource(
    params: GetResourceParams, soar: SOARClient, asset: Asset
) -> GetResourceOutput:
    raise NotImplementedError()


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


class UpdateResourceOutput(ActionOutput):
    id: str = OutputField(
        cef_types=["crits resource id"], example_values=["594813dee1c1dc600ae36138"]
    )
    message: str = OutputField(example_values=["success"])
    return_code: float = OutputField(example_values=[0])
    type: str = OutputField(cef_types=["crits resource"], example_values=["Indicator"])


@app.action(
    description="Update a specified resource",
    action_type="generic",
    read_only=False,
    verbose='The <b>patch_data</b> field expects a json string that will be accepted by the action handler. More information can be found at <a href=\\"https://github.com/crits/crits/wiki/Authenticated-API\\">this link</a>, in the sections about updating TLOs using PATCH.',
)
def update_resource(
    params: UpdateResourceParams, soar: SOARClient, asset: Asset
) -> UpdateResourceOutput:
    raise NotImplementedError()


class CreateResourceParams(Params):
    resource: str = Param(
        description="New Resource Type",
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
    vault_id: str | None = Param(
        description="File to add to resource", primary=True, cef_types=["vault id"]
    )
    source: str = Param(description="The Source of the resource")
    confidence: str | None = Param(
        description="Confidence", value_list=["low", "medium", "high"]
    )
    post_data: str | None = Param(description="Post JSON Data")


class CreateResourceOutput(ActionOutput):
    id: str = OutputField(
        cef_types=["crits resource id"], example_values=["594d8e29e1c1dc600ae36164"]
    )
    message: str = OutputField(example_values=["Success!"])
    return_code: float = OutputField(example_values=[0])
    type: str = OutputField(cef_types=["crits resource"], example_values=["Event"])
    url: str = OutputField(example_values=["/api/v1/events/594d8e29e1c1dc600ae36164/"])


@app.action(
    description="Create a resource",
    action_type="generic",
    read_only=False,
    verbose="All resources expect different fields, save a few common fields. The <b>post_data</b> field expects a JSON string. More information can be found at <a href=\\\"https://github.com/crits/crits/wiki/Authenticated-API\\\">this link</a>. Each resource has a section outlining its specific fields.</br>If no confidence is specified, it will default to \\\"low\\\".<br> Additionally, you can upload files through the vault to be added to the resource. However, not all resource types will accept a file. If you attempt to add a file to a resource that doesn't accept one, then the action will still succeed and a resource will be created, but the attachment will not be added to it. By default, each file will be added as a 'raw' file. If you wish to change this, for example, to upload a zip file, you can set the 'file_format' attribute in the <b>post_data</b> to 'zip'.",
)
def create_resource(
    params: CreateResourceParams, soar: SOARClient, asset: Asset
) -> CreateResourceOutput:
    raise NotImplementedError()


if __name__ == "__main__":
    app.cli()
