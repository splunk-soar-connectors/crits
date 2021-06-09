# --
# File: crits_connector.py
# Copyright (c) 2017-2021 Splunk Inc.
#
# SPLUNK CONFIDENTIAL - Use or disclosure of this material in whole or in part
# without a valid written license from Splunk Inc. is PROHIBITED.

# Phantom imports
import phantom.app as phantom
from phantom.action_result import ActionResult
from phantom.app import BaseConnector
import phantom.rules as phrules

# THIS Connector imports
from crits_consts import *

import json
import requests
from bs4 import BeautifulSoup


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
                "username": config[CRITS_JSON_USERNAME],
                "api_key": config[CRITS_JSON_API_KEY]}

        self._base_url = config[CRITS_JSON_BASE_URL].rstrip('/')

        self._verify = config.get(phantom.APP_JSON_VERIFY, False)

        return phantom.APP_SUCCESS

    def _get_error_message_from_exception(self, e):
        """ This method is used to get appropriate error message from the exception.
        :param e: Exception object
        :return: error message
        """
        error_code = PHANTOM_ERR_CODE_UNAVAILABLE
        error_msg = PHANTOM_ERR_MSG_UNAVAILABLE
        try:
            if hasattr(e, 'args'):
                if len(e.args) > 1:
                    error_code = e.args[0]
                    error_msg = e.args[1]
                elif len(e.args) == 1:
                    error_msg = e.args[0]
        except:
            pass

        return "Error Code: {0}. Error Message: {1}".format(error_code, error_msg)

    def _validate_integer(self, action_result, parameter, key, allow_zero=False):
        if parameter is not None:
            try:
                if not float(parameter).is_integer():
                    return action_result.set_status(phantom.APP_ERROR, CRITS_ERR_INVALID_INT.format(param=key)), None

                parameter = int(parameter)
            except:
                return action_result.set_status(phantom.APP_ERROR, CRITS_ERR_INVALID_INT.format(param=key)), None

            if parameter < 0:
                return action_result.set_status(phantom.APP_ERROR, CRITS_ERR_NEGATIVE_INT_PARAM.format(param=key)), None
            if not allow_zero and parameter == 0:
                return action_result.set_status(phantom.APP_ERROR, CRITS_ERR_INVALID_PARAM.format(param=key)), None

        return phantom.APP_SUCCESS, parameter

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

        if error_text.strip():
            message = "Error from server: Status Code: {0}. Data from server:\n{1}\n".format(status_code, error_text)
        else:
            message = "Error from server: Status Code: {0}".format(status_code)

        message = message.replace('{', '{{').replace('}', '}}')

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _process_json_response(self, r, action_result):

        # Try a json parse
        try:
            resp_json = r.json()
        except Exception as e:
            self.save_progress('Cannot parse JSON')
            return RetVal(action_result.set_status(phantom.APP_ERROR, "Unable to parse response as JSON", self._get_error_message_from_exception(e)), None)

        if 200 <= r.status_code < 205:
            return RetVal(phantom.APP_SUCCESS, resp_json)

        action_result.add_data(resp_json)
        try:
            message = resp_json['error_message']
        except:
            message = r.text.replace('{', '{{').replace('}', '}}')
        return RetVal( action_result.set_status( phantom.APP_ERROR, "Error from server, Status Code: {0} data returned: {1}".format(r.status_code, message)), resp_json)

    def _process_response(self, r, action_result):

        # store the r_text in debug data, it will get dumped in the logs if an error occurs
        if hasattr(action_result, 'add_debug_data'):
            action_result.add_debug_data({'r_status_code': r.status_code})
            action_result.add_debug_data({'r_text': r.text})
            action_result.add_debug_data({'r_headers': r.headers})

        # There are just too many differences in the response to handle all of them in the same function
        if 'json' in r.headers.get('Content-Type', ''):
            return self._process_json_response(r, action_result)

        if 'html' in r.headers.get('Content-Type', ''):
            return self._process_html_response(r, action_result)

        # it's not an html or json, handle if it is a successfull empty reponse
        if (200 <= r.status_code < 205) and (not r.text):
            return self._process_empty_reponse(r, action_result)

        # everything else is actually an error at this point
        message = "Can't process response from server. Status Code: {0} Data from server: {1}".format(
                r.status_code, r.text.replace('{', '{{').replace('}', '}}'))

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _make_rest_call(self, endpoint, action_result, params=None, data=None, headers=None, method="get", files=None, real_data=None):
        """ Returns 2 values, use RetVal """
        if headers is None:
            headers = {}
        if params is None:
            params = {}
        url = self._base_url + endpoint
        params.update(self._params)

        try:
            request_func = getattr(requests, method)
        except AttributeError:
            # Set the action_result status to error, the handler function will most probably return as is
            return RetVal(action_result.set_status(phantom.APP_ERROR, "Unsupported method: {0}".format(method)), None)
        except Exception as e:
            err_msg = self._get_error_message_from_exception(e)
            # Set the action_result status to error, the handler function will most probably return as is
            return RetVal(action_result.set_status(phantom.APP_ERROR, "Handled exception: {0}".format(err_msg)), None)

        try:
            response = request_func(url, params=params, json=data, headers=headers, verify=self._verify, files=files, data=real_data)
        except Exception as e:
            err_msg = self._get_error_message_from_exception(e)
            # Set the action_result status to error, the handler function will most probably return as is
            return RetVal(action_result.set_status(phantom.APP_ERROR, "Error connecting: {0}".format(err_msg.replace(self._params['api_key'], '<api_key>'))), None)

        return self._process_response(response, action_result)

    def _handle_run_query(self, param):

        action_result = self.add_action_result(ActionResult(param))
        query = {}
        endpoint = param.get(CRITS_JSON_NEXT_PAGE)
        # No page URI provided
        if not endpoint:
            resource = param.get(CRITS_JSON_RESOURCE)
            if not resource:
                return action_result.set_status(phantom.APP_ERROR, CRITS_ERR_RUN_QUERY_RESOURCE_REQUIRED)
            query = param.get(CRITS_JSON_QUERY)
            if query:
                # The query is a json
                try:
                    query = json.loads(query)
                except Exception as e:
                    err_msg = self._get_error_message_from_exception(e)
                    return action_result.set_status(phantom.APP_ERROR, CRITS_ERR_INVALID_QUERY_JSON.format(err_msg))
            else:
                query = {}
            # Try for type casts
            ret_val, offset = self._validate_integer(action_result, param.get('offset'), CRITS_OFFSET, allow_zero=True)
            if phantom.is_fail(ret_val):
                return action_result.get_status()
            query['offset'] = offset

            ret_val, limit = self._validate_integer(action_result, param.get('limit'), CRITS_LIMIT)
            if phantom.is_fail(ret_val):
                return action_result.get_status()
            query['limit'] = limit

            endpoint = "/api/v1/{0}/".format(resource)

        # Make the rest endpoint call
        ret_val, response = self._make_rest_call(endpoint, action_result, params=query)

        if phantom.is_fail(ret_val):
            return action_result.get_data()

        total_count = response.get('meta', {}).get('total_count', 0)
        next_page = response.get('meta', {}).get('next')

        action_result.update_summary({'total_results': total_count})
        if next_page:
            action_result.update_summary({'next_page': next_page.replace(self._params['api_key'], '<api_key>')})

        objects = response.get('objects')

        for curr_obj in objects:
            action_result.add_data(curr_obj)

        return action_result.set_status(phantom.APP_SUCCESS)

    def _get_resource(self, param):

        resource = param[CRITS_JSON_RESOURCE]
        res_id = param[CRITS_JSON_ID]

        action_result = self.add_action_result(ActionResult(param))

        endpoint = "/api/v1/{0}/{1}/".format(resource, res_id)

        # Make the rest endpoint call
        ret_val, response = self._make_rest_call(endpoint, action_result)

        if phantom.is_fail(ret_val):
            return action_result.get_data()

        action_result.add_data(response)

        return action_result.set_status(phantom.APP_SUCCESS, CRITS_SUCC_GET_RESOURCE)

    def _update_resource(self, param):

        action_result = self.add_action_result(ActionResult(param))

        resource = param[CRITS_JSON_RESOURCE]
        res_id = param[CRITS_JSON_ID]
        data_str = param[CRITS_JSON_PATCH_DATA]

        try:
            data = json.loads(data_str)
        except Exception as e:
            err_msg = self._get_error_message_from_exception(e)
            return action_result.set_status(phantom.APP_ERROR, CRITS_ERR_INVALID_QUERY_JSON.format(err_msg))

        endpoint = "/api/v1/{0}/{1}/".format(resource, res_id)

        ret_val, response = self._make_rest_call(endpoint, action_result, data=data, method="patch")

        if phantom.is_fail(ret_val):
            return action_result.get_data()

        msg = response.get('message', '')
        if 'success' not in msg.lower():
            return action_result.set_status(phantom.APP_ERROR, "Unable to update resource: {0}".format(msg))

        action_result.add_data(response)

        summary = action_result.update_summary({})
        summary['resource_id'] = res_id

        return action_result.set_status(phantom.APP_SUCCESS, CRITS_SUCC_UPDATE_RESOURCE)

    def _get_filename_filepath(self, action_result, vault_id):

        try:
            success, message, vault_info = phrules.vault_info(vault_id=vault_id)
            vault_info = list(vault_info)[0]
        except IndexError:
            return action_result.set_status(phantom.APP_ERROR, VAULT_ERR_FILE_NOT_FOUND), None
        except Exception:
            return action_result.set_status(phantom.APP_ERROR, VAULT_ERR_INVALID_ID), None

        vault_path = vault_info.get('path')
        if vault_path is None:
            return action_result.set_status(phantom.APP_ERROR, VAULT_ERR_PATH_NOT_FOUND)

        return phantom.APP_SUCCESS, vault_info.get('name'), vault_path

    def _create_resource(self, param):
        action_result = self.add_action_result(ActionResult(param))

        source = param[CRITS_JSON_SOURCE]
        resource = param[CRITS_JSON_RESOURCE]
        data_str = param.get(CRITS_JSON_POST_DATA)
        confidence = param.get(CRITS_JSON_CONFIDENCE, 'low')
        vault_id = param.get(CRITS_JSON_FILE)

        data = {'source': source, 'confidence': confidence}

        if vault_id:
            try:
                ret_val, file_name, file_path = self._get_filename_filepath(action_result, vault_id)
                if phantom.is_fail(ret_val):
                    return ret_val
                files = {
                    'filedata': (file_name, open(file_path, 'rb'))
                }
                data.update({
                    'upload_type': 'file',
                    'file_format': 'raw'
                })
            except Exception as e:
                err_msg = self._get_error_message_from_exception(e)
                return action_result.set_status(phantom.APP_ERROR, "Error reading file: {}".format(err_msg))
        else:
            files = None

        if data_str:
            try:
                add_data = json.loads(data_str)
                data.update(add_data)
            except Exception as e:
                err_msg = self._get_error_message_from_exception(e)
                return action_result.set_status(phantom.APP_ERROR, CRITS_ERR_INVALID_QUERY_JSON.format(err_msg))

        endpoint = "/api/v1/{0}/".format(resource)

        ret_val, response = self._make_rest_call(endpoint, action_result, real_data=data, method="post", files=files)

        if phantom.is_fail(ret_val):
            return action_result.get_data()

        res_id = response.get('id')
        if not res_id:
            return action_result.set_status(phantom.APP_ERROR, "Unable to create resource: {0}".format(response.get('message', '')))

        action_result.add_data(response)

        summary = action_result.update_summary({})
        summary['resource_id'] = res_id

        return action_result.set_status(phantom.APP_SUCCESS, CRITS_SUCC_CREATE_RESOURCE)

    def _test_asset_connectivity(self, param):

        # Progress
        self.save_progress(CRITS_USING_BASE_URL, base_url=self._base_url)

        # set the endpoint
        endpoint = '/api/v1/indicators/'

        # Action result to represent the call
        action_result = ActionResult()

        # Progress message, since it is test connectivity, it pays to be verbose
        self.save_progress(CRITS_MSG_GET_INDICATORS_TEST)

        # Make the rest endpoint call
        ret_val, response = self._make_rest_call(endpoint, action_result)

        # Process errors
        if phantom.is_fail(ret_val):

            # Dump error messages in the log
            self.debug_print(action_result.get_message())

            # Set the status of the complete connector result
            self.set_status(phantom.APP_ERROR, action_result.get_message())

            # Append the message to display
            self.append_to_message(CRITS_ERR_CONNECTIVITY_TEST)

            # return error
            return phantom.APP_ERROR

        total_count = response.get('meta', {}).get('total_count')

        if total_count:
            self.save_progress("Got {0} indicator{1}".format(total_count, 's' if total_count > 1 else ''))

        # Set the status of the connector result
        return self.set_status_save_progress(phantom.APP_SUCCESS, CRITS_SUCC_CONNECTIVITY_TEST)

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

        if action == self.ACTION_ID_RUN_QUERY:
            result = self._handle_run_query(param)
        elif action == self.ACTION_ID_GET_RESOURCE:
            result = self._get_resource(param)
        elif action == self.ACTION_ID_UPDATE_RESOURCE:
            result = self._update_resource(param)
        elif action == self.ACTION_ID_CREATE_RESOURCE:
            result = self._create_resource(param)
        elif action == phantom.ACTION_ID_TEST_ASSET_CONNECTIVITY:
            result = self._test_asset_connectivity(param)

        return result


if __name__ == '__main__':

    import sys
    import pudb

    pudb.set_trace()

    if (len(sys.argv) < 2):
        print("No test json specified as input")
        exit(0)

    with open(sys.argv[1]) as f:
        in_json = f.read()
        in_json = json.loads(in_json)
        print(json.dumps(in_json, indent=4))

        connector = CritsConnector()
        connector.print_progress_message = True
        ret_val = connector._handle_action(json.dumps(in_json), None)
        print(json.dumps(json.loads(ret_val), indent=4))

    exit(0)
