import re
import urllib.parse


ALLOWED_RESOURCES = frozenset(
    {
        "actors", "actoridentifiers", "backdoors", "campaigns", "certificates",
        "domains", "emails", "events", "exploits", "indicators", "ips", "pcaps",
        "raw_data", "samples", "screenshots", "targets",
    }
)


class ValidationError(ValueError):
    pass


def validate_resource(resource: str) -> str:
    if resource not in ALLOWED_RESOURCES:
        raise ValidationError("Invalid CRITs resource")
    return resource


def validate_resource_id(resource_id: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{24}", resource_id):
        raise ValidationError("Resource ID must be a 24-character lowercase hexadecimal value")
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
        raise ValidationError(f"Please provide a valid integer value in the {label}") from error
    if result < 0:
        raise ValidationError(f"Please provide a valid non-negative integer value in the {label}")
    if result == 0 and not allow_zero:
        raise ValidationError(f"Please provide a non-zero positive integer in the {label}")
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
        raise ValidationError("Invalid CRITs next page URI")
    query = urllib.parse.urlencode(
        [
            (key, value)
            for key, value in urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
            if key not in {"username", "api_key"}
        ],
        doseq=True,
    )
    return urllib.parse.urlunsplit(("", "", parsed.path, query, ""))
