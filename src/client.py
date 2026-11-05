import json
from html.parser import HTMLParser
from typing import Any

import httpx


class CritsClientError(Exception):
    """A CRITs API failure with the user-facing legacy connector message."""

    def __init__(
        self,
        message: str,
        *,
        response_data: Any = None,
        has_response_data: bool = False,
    ) -> None:
        super().__init__(message)
        self.response_data = response_data
        self.has_response_data = has_response_data


def _redact(value: str, secret: str) -> str:
    return value.replace(secret, "<api_key>") if secret else value


def _redact_json(value: Any, secret: str) -> Any:
    if isinstance(value, str):
        return _redact(value, secret)
    if isinstance(value, list):
        return [_redact_json(item, secret) for item in value]
    if isinstance(value, dict):
        return {
            _redact(key, secret): _redact_json(item, secret)
            for key, item in value.items()
        }
    return value


class _TextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        value = data.strip()
        if value:
            self.parts.append(value)


def _format_exception(error: Exception) -> str:
    args = error.args
    if len(args) > 1:
        code, message = args[0], args[1]
    elif args:
        code, message = "Error code unavailable", args[0]
    else:
        code, message = "Error code unavailable", "Unknown error occurred. Please check the asset configuration and|or action parameters."
    return f"Error Code: {code}. Error Message: {message}"


class CritsClient:
    def __init__(self, url: str, username: str, api_key: str, verify: bool, timeout: float) -> None:
        self.base_url = url.rstrip("/")
        self.api_key = api_key
        try:
            numeric_timeout = float(timeout)
            if not numeric_timeout.is_integer():
                raise ValueError
            timeout_value = int(numeric_timeout)
        except (TypeError, ValueError, OverflowError) as error:
            raise CritsClientError("Please provide a valid integer value in the 'timeout' action parameter") from error
        if timeout_value < 0:
            raise CritsClientError("Please provide a valid non-negative integer value in the 'timeout' action parameter")
        if timeout_value == 0:
            raise CritsClientError("Please provide a non-zero positive integer in the 'timeout' action parameter")
        self._client = httpx.Client(
            headers={"Authorization": f"ApiKey {username}:{api_key}"},
            verify=verify,
            timeout=timeout_value,
            follow_redirects=True,
        )

    def close(self) -> None:
        self._client.close()

    def request(
        self,
        endpoint: str,
        *,
        method: str = "get",
        params: dict[str, Any] | None = None,
        json_data: Any = None,
        form_data: dict[str, Any] | None = None,
        files: dict[str, tuple[str, Any]] | None = None,
    ) -> Any:
        if method not in {"get", "post", "patch"}:
            raise CritsClientError(f"Unsupported method: {method}")

        try:
            response = self._client.request(
                method.upper(),
                f"{self.base_url}/{endpoint.lstrip('/')}",
                params={key: value for key, value in (params or {}).items() if value is not None},
                json=json_data,
                data=form_data,
                files=files,
            )
        except Exception as error:
            message = _redact(_format_exception(error), self.api_key)
            raise CritsClientError(f"Error connecting: {message}") from error

        content_type = response.headers.get("Content-Type", "")
        if "json" in content_type:
            try:
                data = response.json()
            except Exception as error:
                raise CritsClientError(
                    _redact(f"Unable to parse response as JSON: {_format_exception(error)}", self.api_key)
                ) from error
            if 200 <= response.status_code < 205:
                return data
            message = data.get("error_message") if isinstance(data, dict) else None
            if not message:
                message = response.text.replace("{", "{{").replace("}", "}}")
            message = _redact(str(message), self.api_key)
            safe_data = _redact_json(data, self.api_key)
            raise CritsClientError(
                f"Error from server, Status Code: {response.status_code} data returned: {message}",
                response_data=safe_data,
                has_response_data=True,
            )

        if "html" in content_type:
            parser = _TextParser()
            try:
                parser.feed(response.text)
                error_text = "\n".join(parser.parts)
            except Exception:
                error_text = "Cannot parse error details"
            message = f"Error from server: Status Code: {response.status_code}"
            if error_text:
                message += f". Data from server:\n{error_text}\n"
            raise CritsClientError(_redact(message.replace("{", "{{").replace("}", "}}"), self.api_key))

        if 200 <= response.status_code < 205 and not response.text:
            raise CritsClientError("The server returned an empty response")
        message = "Can't process response from server. Status Code: {} Data from server: {}".format(
            response.status_code, response.text.replace("{", "{{").replace("}", "}}")
        )
        raise CritsClientError(_redact(message, self.api_key))


def parse_json_object(value: str, field: str) -> dict[str, Any]:
    try:
        parsed = json.loads(value)
    except Exception as error:
        raise CritsClientError(f"Failed to load the query json. Error: {_format_exception(error)}") from error
    if not isinstance(parsed, dict):
        raise CritsClientError(f"Failed to load the query json. Error: Expected a JSON object for {field}")
    return parsed
