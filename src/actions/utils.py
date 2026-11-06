import json
import re
import urllib.parse
from typing import Any


ALLOWED_RESOURCES = frozenset(
    {
        "actors", "actoridentifiers", "backdoors", "campaigns", "certificates",
        "domains", "emails", "events", "exploits", "indicators", "ips", "pcaps",
        "raw_data", "samples", "screenshots", "targets",
    }
)


def validate_resource(resource: str) -> str:
    if resource not in ALLOWED_RESOURCES:
        raise ValueError("Invalid CRITs resource")
    return resource


def validate_resource_id(resource_id: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{24}", resource_id):
        raise ValueError("Resource ID must be a 24-character lowercase hexadecimal value")
    return resource_id


def validate_integer(value: int | float | str | None, label: str, *, allow_zero: bool = False) -> int | None:
    if value is None:
        return None
    try:
        number = float(value)
        if not number.is_integer():
            raise ValueError
        result = int(number)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"Please provide a valid integer value in the {label}") from error
    if result < 0:
        raise ValueError(f"Please provide a valid non-negative integer value in the {label}")
    if result == 0 and not allow_zero:
        raise ValueError(f"Please provide a non-zero positive integer in the {label}")
    return result


def validate_next_page(next_page: str) -> str:
    parsed = urllib.parse.urlsplit(next_page)
    path_parts = parsed.path.split("/")
    if (
        parsed.scheme
        or parsed.netloc
        or parsed.fragment
        or "%" in parsed.path
        or len(path_parts) < 5
        or path_parts[:3] != ["", "api", "v1"]
        or path_parts[3] not in ALLOWED_RESOURCES
        or any(part == ".." for part in path_parts)
    ):
        raise ValueError("Invalid CRITs next page URI")
    query = urllib.parse.urlencode(
        [
            (key, value)
            for key, value in urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
            if key not in {"username", "api_key"}
        ],
        doseq=True,
    )
    return urllib.parse.urlunsplit(("", "", parsed.path, query, ""))


def parse_json_object(value: str, field: str) -> dict[str, Any]:
    try:
        parsed = json.loads(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"Failed to load the {field} json. Error: {error}") from error
    if not isinstance(parsed, dict):
        raise ValueError(f"Failed to load the {field} json. Error: Expected a JSON object for {field}")
    return parsed


def validate_timeout(timeout: float) -> int:
    try:
        numeric_timeout = float(timeout)
        if not numeric_timeout.is_integer():
            raise ValueError
        timeout_value = int(numeric_timeout)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("Please provide a valid integer value in the 'timeout' action parameter") from error
    if timeout_value < 0:
        raise ValueError("Please provide a valid non-negative integer value in the 'timeout' action parameter")
    if timeout_value == 0:
        raise ValueError("Please provide a non-zero positive integer in the 'timeout' action parameter")
    return timeout_value


def redact(value: str, secret: str) -> str:
    return value.replace(secret, "<api_key>") if secret else value


def redact_data(value: Any, secret: str) -> Any:
    if isinstance(value, str):
        return redact(value, secret)
    if isinstance(value, list):
        return [redact_data(item, secret) for item in value]
    if isinstance(value, dict):
        return {redact(key, secret): redact_data(item, secret) for key, item in value.items()}
    return value
