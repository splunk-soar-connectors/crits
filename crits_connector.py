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
from phantom.action_result import ActionResult
from phantom.app import BaseConnector

# THIS Connector imports
import crits_consts as consts

import json
import requests
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings()


class RetVal(tuple):
    def __new__(cls, val1, val2):
        return tuple.__new__(RetVal, (val1, val2))


class CritsConnector(BaseConnector):

    ACTION_ID_RUN_QUERY = "run_query"
    ACTION_ID_GET_RESOURCE = "get_resource"
    ACTION_ID_UPDATE_RESOURCE = "update_resource"
    ACTION_ID_CREATE_RESOURCE = "create_resource"

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

        return phantom.APP_SUCCESS

    def _process_empty_reponse(self, response, action_result):
        return RetVal(action_result.set_status(phantom.APP_ERROR), None)

    def _process_html_response(self, response, action_result):

        # An html response, is bound to be an error
        status_code = response.status_code

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            error_text = soup.text
            split_lines = error_text.split('\n')
            split_lines = [x.strip() for x in split_lines if x.strip()]
            error_text = '\n'.join(split_lines)
        except:
            error_text = "Cannot parse error details"

        message = "Status Code: {0}. Data from server:\n{1}\n".format(status_code,
                error_text)

        message = message.replace('{', '{{').replace('}', '}}')

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _process_json_response(self, r, action_result):

        # Try a json parse
        try:
            resp_json = r.json()
        except Exception as e:
            self.save_progress('Cannot parse JSON')
            return RetVal(action_result.set_status(phantom.APP_ERROR, "Unable to parse response as JSON", e), None)

        if (200 <= r.status_code < 205):
            return RetVal(phantom.APP_SUCCESS, resp_json)

        action_result.add_data(resp_json)
        message = r.text.replace('{', '{{').replace('}', '}}')
        return RetVal( action_result.set_status( phantom.APP_ERROR, "Error from server, Status Code: {0} data returned: {1}".format(r.status_code, message)), resp_json)

    def _process_response(self, r, action_result):

        # store the r_text in debug data, it will get dumped in the logs if an error occurs
        if hasattr(action_result, 'add_debug_data'):
            action_result.add_debug_data({'r_status_code': r.status_code})
            action_result.add_debug_data({'r_text': r.text})
            action_result.add_debug_data({'r_headers': r.headers})

        # There are just too many differences in the response to handle all of them in the same function
        if ('json' in r.headers.get('Content-Type', '')):
            return self._process_json_response(r, action_result)

        if ('html' in r.headers.get('Content-Type', '')):
            return self._process_html_response(r, action_result)

        # it's not an html or json, handle if it is a successfull empty reponse
        if (200 <= r.status_code < 205) and (not r.text):
            return self._process_empty_reponse(r, action_result)

        # everything else is actually an error at this point
        message = "Can't process response from server. Status Code: {0} Data from server: {1}".format(
                r.status_code, r.text.replace('{', '{{').replace('}', '}}'))

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _make_rest_call(self, endpoint, action_result, params={}, data=None, headers={}, method="get"):
        """ Returns 2 values, use RetVal """
        url = self._base_url + endpoint
        params.update(self._params)

        try:
            request_func = getattr(requests, method)
        except AttributeError:
            # Set the action_result status to error, the handler function will most probably return as is
            return RetVal(action_result.set_status(phantom.APP_ERROR, "Unsupported method: {0}".format(method)), None)
        except Exception as e:
            # Set the action_result status to error, the handler function will most probably return as is
            return RetVal(action_result.set_status(phantom.APP_ERROR, "Handled exception: {0}".format(str(e))), None)

        try:
            response = request_func(url, params=params, json=data, headers=headers)
        except Exception as e:
            # Set the action_result status to error, the handler function will most probably return as is
            return RetVal(action_result.set_status(phantom.APP_ERROR, "Error connecting: {0}".format(str(e))), None)

        self.debug_print(response.url)

        return self._process_response(response, action_result)

    def _handle_run_query(self, param):

        action_result = self.add_action_result(ActionResult(param))
        query = {}
        endpoint = param.get(consts.CRITS_JSON_NEXT_PAGE)
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
            # Try for type casts
            try:
                if 'offset' in param:
                    query['offset'] = int(param.get('offset'))
                if 'limit' in param:
                    query['limit'] = int(param.get('limit'))
            except Exception as e:
                # Since the type of these parameters is already numeric, we probably shouldn't end up here
                return action_result.set_status(phantom.APP_ERROR, "Invalid offset or limit: Value must be numeric")


            endpoint = "/api/v1/{0}/".format(resource)

        self.debug_print(query)

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

        action_result = self.add_action_result(ActionResult(param))

        endpoint = "/api/v1/{0}/{1}/".format(resource, res_id)

        # Make the rest endpoint call
        ret_val, response = self._make_rest_call(endpoint, action_result)

        if (phantom.is_fail(ret_val)):
            return action_result.get_data()

        action_result.add_data(response)

        return action_result.set_status(phantom.APP_SUCCESS)

    def _update_resource(self, param):

        action_result = self.add_action_result(ActionResult(param))

        resource = param[consts.CRITS_JSON_RESOURCE]
        res_id = param[consts.CRITS_JSON_ID]
        data_str = param[consts.CRITS_JSON_PATCH_DATA]

        try:
            data = json.loads(data_str)
        except Exception as e:
            return action_result.set_status(phantom.APP_ERROR, "Failed to load the query json. Error: {0}".format(str(e)))

        endpoint = "/api/v1/{0}/{1}/".format(resource, res_id)

        ret_val, response = self._make_rest_call(endpoint, action_result, data=data, method="patch")

        if (phantom.is_fail(ret_val)):
            return action_result.get_data()

        msg = response.get('message', '')
        if 'success' not in msg.lower():
            return action_result.set_status(phantom.APP_ERROR, "Unable to create resource: {0}".format(msg))

        action_result.add_data(response)

        return action_result.set_status(phantom.APP_SUCCESS)

    def _create_resource(self, param):
        action_result = self.add_action_result(ActionResult(param))

        source = param[consts.CRITS_JSON_SOURCE]
        resource = param[consts.CRITS_JSON_RESOURCE]
        data_str = param.get(consts.CRITS_JSON_POST_DATA)
        confidence = param.get(consts.CRITS_JSON_CONFIDENCE, 'low')

        data = {}
        data['source'] = source
        data['confidence'] = confidence

        if data_str:
            try:
                add_data = json.loads(data_str)
                data.update(add_data)
            except Exception as e:
                return action_result.set_status(phantom.APP_ERROR, "Failed to load the query json. Error: {0}".format(str(e)))

        endpoint = "/api/v1/{0}/".format(resource)

        ret_val, response = self._make_rest_call(endpoint, action_result, data=data, method="post")
        self.debug_print(response)

        if (phantom.is_fail(ret_val)):
            return action_result.get_data()

        res_id = response.get('id')
        if not res_id:
            return action_result.set_status(phantom.APP_ERROR, "Unable to create resource: {0}".format(response.get('msg', '')))

        action_result.add_data(response)

        return action_result.set_status(phantom.APP_SUCCESS)

    def _test_asset_connectivity(self, param):

        # Progress
        self.save_progress(consts.CRITS_USING_BASE_URL, base_url=self._base_url)

        # set the endpoint
        endpoint = '/api/v1/indicators/'

        # Action result to represent the call
        action_result = ActionResult()

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
        elif (action == self.ACTION_ID_UPDATE_RESOURCE):
            result = self._update_resource(param)
        elif (action == self.ACTION_ID_CREATE_RESOURCE):
            result = self._create_resource(param)
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
