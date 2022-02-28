# File: crits_consts.py
#
# Copyright (c) 2017-2022 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.
PHANTOM_ERR_CODE_UNAVAILABLE = "Error code unavailable"
PHANTOM_ERR_MSG_UNAVAILABLE = "Unknown error occurred. Please check the asset configuration and|or action parameters."

# Success/Error status and messages
CRITS_SUCC_QUERY_EXECUTED = "Executed query"
CRITS_SUCC_CONNECTIVITY_TEST = "Test connectivity passed"
CRITS_ERR_CONNECTIVITY_TEST = "Test connectivity failed"
CRITS_SUCC_GET_RESOURCE = "Successfully retrieved resource"
CRITS_SUCC_CREATE_RESOURCE = "Successfully created new resource"
CRITS_SUCC_UPDATE_RESOURCE = "Successfully updated resource"

# Json keys
CRITS_JSON_ID = "id"
CRITS_JSON_QUERY = "query"
CRITS_JSON_SOURCE = "source"
CRITS_JSON_API_KEY = "api_key"
CRITS_JSON_BASE_URL = "url"
CRITS_JSON_RESOURCE = "resource"
CRITS_JSON_USERNAME = "username"
CRITS_JSON_NEXT_PAGE = "next_page"
CRITS_JSON_POST_DATA = "post_data"
CRITS_JSON_PATCH_DATA = "patch_data"
CRITS_JSON_CONFIDENCE = "confidence"
CRITS_JSON_FILE = "vault_id"
CRITS_OFFSET = "'offset' action parameter"
CRITS_LIMIT = "'limit' action parameter"

CRITS_ERR_API_UNSUPPORTED_METHOD = "Unsupported method: {method} called"
CRITS_ERR_SERVER_CONNECTION = "Error connecting to server"
CRITS_ERR_JSON_PARSE = "Unable to parse response as JSON. From server: {raw_text}"
CRITS_ERR_FROM_SERVER = "Error from server, Status code: {status}, details: {details}"
CRITS_USING_BASE_URL = "Using url: {base_url}"
CRITS_MSG_GET_INDICATORS_TEST = "Querying recent indicators to check credentials"
CRITS_ERR_RUN_QUERY_RESOURCE_REQUIRED = "Parameter 'resource' is required"
CRITS_ERR_INVALID_OFFSET_OR_LIMIT = "Invalid offset or limit: Value must be numeric"
CRITS_ERR_INVALID_QUERY_JSON = "Failed to load the query json. Error: {0}"
CRITS_ERR_INVALID_INT = "Please provide a valid integer value in the {param}"
CRITS_ERR_NEGATIVE_INT_PARAM = "Please provide a valid non-negative integer value in the {param}"
CRITS_ERR_INVALID_PARAM = "Please provide a non-zero positive integer in the {param}"

VAULT_ERR_FILE_NOT_FOUND = "Vault file could not be found with supplied Vault ID"
VAULT_ERR_INVALID_ID = "Vault ID not valid"
VAULT_ERR_PATH_NOT_FOUND = "Could not find a path associated with the provided vault ID"

DEFAULT_REQUEST_TIMEOUT = 30  # in seconds
