import httpx
from soar_sdk.action_results import ActionOutput, ActionResult, OutputField, PermissiveActionOutput
from soar_sdk.auth import StaticTokenAuth
from soar_sdk.params import Param, Params
from soar_sdk.abstract import SOARClient
from soar_sdk.exceptions import ActionFailure

from ..asset import Asset
from .utils import parse_json_object, redact, redact_data, validate_integer, validate_next_page, validate_resource, validate_timeout


class RunQueryParams(Params):
    resource: str | None = Param(
        description="Resource to query on. Required if no Page URI is present",
        primary=True,
        value_list=["actors", "actoridentifiers", "backdoors", "campaigns", "certificates", "domains", "emails", "events", "exploits", "indicators", "ips", "pcaps", "raw_data", "samples", "screenshots", "targets"],
        cef_types=["crits resource"],
    )
    query: str | None = Param(description="Query to run", primary=True, cef_types=["crits query"])
    limit: float | None = Param(description="Results per page")
    offset: float | None = Param(description="Paging offset")
    next_page: str | None = Param(description="Next page URI")


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


class RunQueryOutput(PermissiveActionOutput):
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


def run_query(params: RunQueryParams, soar: SOARClient, asset: Asset) -> list[RunQueryOutput]:
    try:
        if params.next_page:
            endpoint = validate_next_page(params.next_page)
            query = None
        else:
            if not params.resource:
                raise ValueError("Parameter 'resource' is required")
            resource = validate_resource(params.resource)
            query = parse_json_object(params.query, "query") if params.query else {}
            query["offset"] = validate_integer(params.offset, "'offset' action parameter", allow_zero=True)
            query["limit"] = validate_integer(params.limit, "'limit' action parameter")
            endpoint = f"/api/v1/{resource}/"
    except ValueError as error:
        raise ActionFailure(str(error)) from error

    try:
        timeout = validate_timeout(asset.timeout)
    except ValueError as error:
        raise ActionFailure(str(error)) from error
    
    auth = StaticTokenAuth(f"{asset.username}:{asset.api_key}", token_type="ApiKey")
    client = httpx.Client(
        auth=auth,
        verify=asset.verify_server_cert,
        timeout=timeout,
        follow_redirects=True,
    )

    try:
        response = client.get(
            f"{asset.url.rstrip('/')}/{endpoint.lstrip('/')}",
            params={key: value for key, value in (query or {}).items() if value is not None},
        )
    except httpx.HTTPError as error:
        raise ActionFailure(f"Error connecting: {redact(str(error), asset.api_key)}") from error
    finally:
        client.close()

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as error:
        response = error.response
        content_type = response.headers.get("Content-Type", "")
        if "json" not in content_type:
            message = "Can't process response from server. Status Code: {} Data from server: {}".format(
                response.status_code, response.text.replace("{", "{{").replace("}", "}}")
            )
            raise ActionFailure(redact(message, asset.api_key)) from error
        try:
            response_data = response.json()
        except ValueError as parse_error:
            raise ActionFailure(
                f"Unable to parse response as JSON: {redact(str(parse_error), asset.api_key)}"
            ) from parse_error
        message = response_data.get("error_message") if isinstance(response_data, dict) else None
        if not message:
            message = response.text.replace("{", "{{").replace("}", "}}")
        result = ActionResult(
            status=False,
            message=redact(f"Error from server, Status Code: {response.status_code} data returned: {message}", asset.api_key),
        )
        result.add_data(redact_data(response_data, asset.api_key))
        return result  # type: ignore[return-value]

    if "json" not in response.headers.get("Content-Type", ""):
        if 200 <= response.status_code < 205 and not response.text:
            raise ActionFailure("The server returned an empty response")
        message = "Can't process response from server. Status Code: {} Data from server: {}".format(
            response.status_code, response.text.replace("{", "{{").replace("}", "}}")
        )
        raise ActionFailure(redact(message, asset.api_key))
    try:
        response_data = response.json()
    except ValueError as error:
        raise ActionFailure(f"Unable to parse response as JSON: {redact(str(error), asset.api_key)}") from error
    if response.status_code == 205:  # Preserve the legacy 200-204 success range.
        message = response_data.get("error_message") if isinstance(response_data, dict) else None
        if not message:
            message = response.text.replace("{", "{{").replace("}", "}}")
        result = ActionResult(
            status=False,
            message=redact(f"Error from server, Status Code: {response.status_code} data returned: {message}", asset.api_key),
        )
        result.add_data(redact_data(response_data, asset.api_key))
        return result  # type: ignore[return-value]

    if not isinstance(response_data, dict):
        raise ActionFailure("CRITs query response was not a JSON object")
    meta = response_data.get("meta") or {}
    next_page = meta.get("next") if isinstance(meta, dict) else None
    if next_page and asset.api_key:
        next_page = str(next_page).replace(asset.api_key, "<api_key>")
    soar.set_summary(RunQuerySummary(total_results=(meta.get("total_count", 0) if isinstance(meta, dict) else 0), next_page=next_page))
    soar.set_message("Executed query")
    objects = response_data.get("objects") or []
    return [RunQueryOutput.model_validate(item) for item in objects]
