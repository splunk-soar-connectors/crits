from soar_sdk.action_results import ActionResult

from src.client import CritsClientError


def failed_client_result(error: CritsClientError) -> ActionResult:
    result = ActionResult(status=False, message=str(error))
    if error.has_response_data:
        result.add_data(error.response_data)
    return result
