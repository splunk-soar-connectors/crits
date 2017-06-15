# --
# File: crits_connector.py
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

# Phantom imports
import phantom.app as phantom

# THIS Connector imports
import crits_consts as consts

import json
import requests

requests.packages.urllib3.disable_warnings()


class CritsConnector(phantom.BaseConnector):

    ACTION_ID_RUN_QUERY = "run_query"
    ACTION_ID_GET_RESOURCE = "get_resource"

    def __init__(self):

        # Call the BaseConnectors init first
        super(CritsConnector, self).__init__()

        self._params = None

    def initialize(self):

        config = self.get_config()

        self._params = {
                "username": config[consts.CRITS_JSON_USERNAME],
                "api_key": config[consts.CRITS_JSON_API_KEY]}

        self._base_url = config[consts.CRITS_JSON_BASE_URL].rstrip('/')

        # self._base_url += "/api/v1"

        return phantom.APP_SUCCESS

    def _make_rest_call(self, endpoint, action_result, params=None, data=None, method="get"):
        """ Function that makes the REST call to the device, generic function that can be called from various action handlers"""

        # Get the config
        config = self.get_config()

        resp_json = None

        if (params is None):
            params = dict()

        # if (not endpoint.endswith('/')):
        #     endpoint += '/'

        params.update(self._params)

        # get or post or put, whatever the caller asked us to use, if not specified the default will be 'get'
        request_func = getattr(requests, method)

        # handle the error in case the caller specified a non-existant method
        if (not request_func):
            action_result.set_status(phantom.APP_ERROR, consts.CRITS_ERR_API_UNSUPPORTED_METHOD.format(method=method))

        # Make the call
        try:
            r = request_func(self._base_url + endpoint, verify=config[phantom.APP_JSON_VERIFY], params=params)
        except Exception as e:
            return (action_result.set_status(phantom.APP_ERROR, consts.CRITS_ERR_SERVER_CONNECTION, e), resp_json)

        # self.debug_print('REST url: {0}'.format(r.url))

        # Try a json parse, since most REST API's give back the data in json, if the device does not return JSONs, then need to implement parsing them some other manner
        try:
            resp_json = r.json()
        except Exception as e:
            # r.text is guaranteed to be NON None, it will be empty, but not None
            msg_string = consts.CRITS_ERR_JSON_PARSE.format(raw_text=r.text)
            return (action_result.set_status(phantom.APP_ERROR, msg_string, e), resp_json)

        # Handle any special HTTP error codes here, many devices return an HTTP error code like 204. The requests module treats these as error,
        # so handle them here before anything else, uncomment the following lines in such cases
        # if (r.status_code == 201):
        #     return (phantom.APP_SUCCESS, resp_json)

        # Handle/process any errors that we get back from the device
        if (200 <= r.status_code <= 399):
            # Success
            return (phantom.APP_SUCCESS, resp_json)

        # Failure
        action_result.add_data(resp_json)

        details = json.dumps(resp_json).replace('{', '').replace('}', '')

        return (action_result.set_status(phantom.APP_ERROR, consts.CRITS_ERR_FROM_SERVER.format(status=r.status_code, detail=details)), resp_json)

    def _handle_run_query(self, param):

        action_result = self.add_action_result(phantom.ActionResult(param))
        query = None
        endpoint = param.get(consts.CRIT_JSON_NEXT_PAGE)
        # No page URI provided
        if not endpoint:
            resource = param.get(consts.CRITS_JSON_RESOURCE)
            if not resource:
                return action_result.set_status(phantom.APP_ERROR, "Parameter 'resource' is required")
            query = param.get(consts.CRITS_JSON_QUERY)
            if (query):
                # The query is a json
                try:
                    query = json.loads(query)
                except Exception as e:
                    return action_result.set_status(phantom.APP_ERROR, "Failed to load the query json. Error: {0}".format(str(e)))
            else:
                query = {}
            query['offset'] = int(param.get('offset', 0))
            query['limit'] = int(param.get('limit', 0))
            endpoint = "/api/v1/{0}/".format(resource)

        # Make the rest endpoint call
        ret_val, response = self._make_rest_call(endpoint, action_result, params=query)

        if (phantom.is_fail(ret_val)):
            return action_result.get_data()

        total_count = response.get('meta', {}).get('total_count', 0)
        next_page = response.get('meta', {}).get('next')

        action_result.update_summary({'total_results': total_count})
        if next_page:
            action_result.update_summary({'next_page': next_page})

        objects = response.get('objects')

        for curr_obj in objects:
            action_result.add_data(curr_obj)

        return action_result.set_status(phantom.APP_SUCCESS)

    def _get_resource(self, param):

        resource = param[consts.CRITS_JSON_RESOURCE]
        res_id = param[consts.CRITS_JSON_ID]

        action_result = self.add_action_result(phantom.ActionResult(param))

        endpoint = "/api/v1/{0}/{1}/".format(resource, res_id)

        # Make the rest endpoint call
        ret_val, response = self._make_rest_call(endpoint, action_result)

        if (phantom.is_fail(ret_val)):
            return action_result.get_data()

        action_result.add_data(response)

        return action_result.set_status(phantom.APP_SUCCESS)

    def _test_asset_connectivity(self, param):

        # Progress
        self.save_progress(consts.CRITS_USING_BASE_URL, base_url=self._base_url)

        # set the endpoint
        endpoint = '/api/v1/indicators/'

        # Action result to represent the call
        action_result = phantom.ActionResult(param)

        # Progress message, since it is test connectivity, it pays to be verbose
        self.save_progress(consts.CRITS_MSG_GET_INDICATORS_TEST)

        # Make the rest endpoint call
        ret_val, response = self._make_rest_call(endpoint, action_result)

        # Process errors
        if (phantom.is_fail(ret_val)):

            # Dump error messages in the log
            self.debug_print(action_result.get_message())

            # Set the status of the complete connector result
            self.set_status(phantom.APP_ERROR, action_result.get_message())

            # Append the message to display
            self.append_to_message(consts.CRITS_ERR_CONNECTIVITY_TEST)

            # return error
            return phantom.APP_ERROR

        total_count = response.get('meta', {}).get('total_count')

        if (total_count):
            self.save_progress("Got {0} indicator{1}".format(total_count, 's' if total_count > 1 else ''))

        # Set the status of the connector result
        return self.set_status_save_progress(phantom.APP_SUCCESS, consts.CRITS_SUCC_CONNECTIVITY_TEST)

    def handle_action(self, param):
        """Function that handles all the actions

            Args:
                The json containing config, action and supporting parameters
                Handle to the ph_connector, should be used/passed when making ph_connector function calls

            Return:
                status code
        """

        # Get the action that we are supposed to carry out, set it in the connection result object
        action = self.get_action_identifier()

        result = phantom.APP_SUCCESS

        if (action == self.ACTION_ID_RUN_QUERY):
            result = self._handle_run_query(param)
        elif (action == self.ACTION_ID_GET_RESOURCE):
            result = self._get_resource(param)
        elif (action == phantom.ACTION_ID_TEST_ASSET_CONNECTIVITY):
            result = self._test_asset_connectivity(param)

        return result


if __name__ == '__main__':

    import sys
    import pudb

    pudb.set_trace()

    if (len(sys.argv) < 2):
        print "No test json specified as input"
        exit(0)

    with open(sys.argv[1]) as f:
        in_json = f.read()
        in_json = json.loads(in_json)
        print(json.dumps(in_json, indent=4))

        connector = CritsConnector()
        connector.print_progress_message = True
        ret_val = connector._handle_action(json.dumps(in_json), None)
        print json.dumps(json.loads(ret_val), indent=4)

    exit(0)
