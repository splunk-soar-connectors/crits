# --
# File: crits_consts.py
#
# Copyright (c) Phantom Cyber Corporation, 2017
#
# This unpublished material is proprietary to Phantom Cyber.
# All rights reserved. The methods and
# techniques described herein are considered trade secrets
# and/or confidential. Reproduction or distribution, in whole
# or in part, is forbidden except by express written permission
# of Phantom Cyber Corporation.
#
# --

# Success/Error status and messages
CRITS_SUCC_QUERY_EXECUTED = "Executed query"
CRITS_SUCC_CONNECTIVITY_TEST = "Connectivity test passed"
CRITS_ERR_CONNECTIVITY_TEST = "Connectivity test failed"

# Json keys
CRITS_JSON_QUERY = "query"
CRITS_JSON_USERNAME = "username"
CRITS_JSON_API_KEY = "api_key"
CRITS_JSON_BASE_URL = "url"
CRITS_JSON_RESOURCE = "resource"
CRITS_JSON_ID = "id"
CRIT_JSON_NEXT_PAGE = "next_page"

CRITS_ERR_API_UNSUPPORTED_METHOD = "Unsupported method: {method} called"
CRITS_ERR_SERVER_CONNECTION = "Error connecting to server"
CRITS_ERR_JSON_PARSE = "Unable to parse response as JSON. From server: {raw_text}"
CRITS_ERR_FROM_SERVER = "Error from server, Status code: {status}, details: {details}"
CRITS_USING_BASE_URL = "Using url: {base_url}"
CRITS_MSG_GET_INDICATORS_TEST = "Querying recent indicators to check credentials"
