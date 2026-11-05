from typing import Any

from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, OutputField, PermissiveActionOutput
from soar_sdk.exceptions import ActionFailure
from soar_sdk.params import Param, Params

from src.asset import Asset
from src.client import CritsClient, CritsClientError, parse_json_object
from src.actions._validators import ValidationError, validate_resource
from src.actions._results import failed_client_result


class CreateResourceParams(Params):
    resource: str = Param(description="New Resource Type", primary=True, value_list=["actors", "actoridentifiers", "backdoors", "campaigns", "certificates", "domains", "emails", "events", "exploits", "indicators", "ips", "pcaps", "raw_data", "samples", "screenshots", "targets"], cef_types=["crits resource"])
    vault_id: str | None = Param(description="File to add to resource", primary=True, cef_types=["vault id"])
    source: str = Param(description="The Source of the resource")
    confidence: str | None = Param(description="Confidence", value_list=["low", "medium", "high"])
    post_data: str | None = Param(description="Post JSON Data")


class CreateResourceOutput(PermissiveActionOutput):
    id: str | None = OutputField(cef_types=["crits resource id"])
    message: str | None = None
    return_code: float | None = None
    type: str | None = OutputField(cef_types=["crits resource"])
    url: str | None = None


def _get_vault_file(soar: SOARClient, vault_id: str) -> tuple[str, Any]:
    try:
        attachments = soar.vault.get_attachment(vault_id=vault_id)
        attachment = next(iter(attachments))
    except StopIteration as error:
        raise ValueError("Vault file could not be found with supplied Vault ID") from error
    except Exception as error:
        raise ValueError("Vault ID not valid") from error
    if not attachment.path:
        raise ValueError("Could not find a path associated with the provided vault ID")
    try:
        return attachment.name, attachment.open("rb")
    except Exception as error:
        raise ValueError(f"Error reading file: {error}") from error


def create_resource(params: CreateResourceParams, soar: SOARClient, asset: Asset) -> list[CreateResourceOutput]:
    client: CritsClient | None = None
    file_data = None
    try:
        resource = validate_resource(params.resource)
        data: dict[str, Any] = {
            "source": params.source,
            "confidence": "low" if params.confidence is None else params.confidence,
        }
        extra_data = parse_json_object(params.post_data, "post_data") if params.post_data else {}

        upload = None
        if params.vault_id:
            file_name, file_data = _get_vault_file(soar, params.vault_id)
            upload = {"filedata": (file_name, file_data)}
            data.update({"upload_type": "file", "file_format": "raw"})

        data.update(extra_data)
        client = CritsClient(asset.url, asset.username, asset.api_key, asset.verify_server_cert, asset.timeout)
        response = client.request(f"/api/v1/{resource}/", method="post", form_data=data, files=upload)
    except CritsClientError as error:
        if error.has_response_data:
            return failed_client_result(error)  # type: ignore[return-value]
        raise ActionFailure(str(error)) from error
    except ValidationError as error:
        raise ActionFailure(str(error)) from error
    except ValueError as error:
        raise ActionFailure(str(error)) from error
    except Exception as error:
        raise ActionFailure(f"Error reading file: {error}") from error
    finally:
        if client is not None:
            client.close()
        if file_data is not None:
            file_data.close()

    resource_id = response.get("id") if isinstance(response, dict) else None
    if not resource_id:
        message = response.get("message", "") if isinstance(response, dict) else ""
        if asset.api_key:
            message = str(message).replace(asset.api_key, "<api_key>")
        raise ActionFailure(f"Unable to create resource: {message}")
    soar.set_summary(CreateResourceSummary(resource_id=str(resource_id)))
    soar.set_message("Successfully created new resource")
    return [CreateResourceOutput.model_validate(response)]


class CreateResourceSummary(ActionOutput):
    resource_id: str
