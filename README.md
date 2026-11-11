# CRITs

Publisher: Splunk <br>
Connector Version: 4.0.0 <br>
Product Vendor: MITRE <br>
Product Name: CRITs <br>
Minimum Product Version: 7.0.0

This App supports various investigative actions on CRITs

## Port Information

The app uses HTTP/ HTTPS protocol for communicating with the CRITs server. Below are the default
ports used by Splunk SOAR.

|         Service Name | Transport Protocol | Port |
|----------------------|--------------------|------|
|         http | tcp | 80 |
|         https | tcp | 443 |

### Configuration variables

This table lists the configuration variables required to operate CRITs. These variables are specified when configuring a CRITs asset in Splunk SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**url** | required | string | Device URL e.g. https://mycrits.contoso.com:8080 |
**verify_server_cert** | optional | boolean | Verify server certificate |
**username** | required | string | Username |
**api_key** | required | password | API Key |
**timeout** | optional | numeric | Request Timeout (Default: 30 seconds) |

### Supported Actions

[test connectivity](#action-test-connectivity) - test connectivity <br>
[make request](#action-make-request) - make request <br>
[run query](#action-run-query) - Run a search query on the CRITs device <br>
[get resource](#action-get-resource) - Get a specific resource from CRITs <br>
[update resource](#action-update-resource) - Update a specified resource <br>
[create resource](#action-create-resource) - Create a resource

## action: 'test connectivity'

test connectivity

Type: **test** <br>
Read only: **True**

Basic test for app.

#### Action Parameters

No parameters are required for this action

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'make request'

make request

Type: **generic** <br>
Read only: **False**

'make request' action for the app. Used to handle arbitrary HTTP requests with the app's asset

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**http_method** | required | The HTTP method to use for the request. | string | |
**endpoint** | required | The endpoint to send the request to. | string | |
**headers** | optional | The headers to send with the request (JSON object). An example is {'Content-Type': 'application/json'} | string | |
**query_parameters** | optional | Parameters to append to the URL (JSON object or query string). An example is ?key=value&key2=value2 | string | |
**body** | optional | The body to send with the request (JSON object). An example is {'key': 'value', 'key2': 'value2'} | string | |
**timeout** | optional | The timeout for the request in seconds. | numeric | |
**verify_ssl** | optional | Whether to verify the SSL certificate. Default is True. | boolean | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.http_method | string | | |
action_result.parameter.endpoint | string | | |
action_result.parameter.headers | string | | |
action_result.parameter.query_parameters | string | | |
action_result.parameter.body | string | | |
action_result.parameter.timeout | numeric | | |
action_result.parameter.verify_ssl | boolean | | |
action_result.data.\*.status_code | numeric | | 200 404 500 |
action_result.data.\*.response_body | string | | {"key": "value"} |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'run query'

Run a search query on the CRITs device

Type: **investigate** <br>
Read only: **True**

Query on CRITs is made up of multiple instances of key-value pairs, much like the parameters that are specified to an HTTP URL. To keep things simple, the action takes as input each parameter and its value to match as a JSON dictionary (in string form).<br>For example to search for an indicator of value <b>baddomain.com</b>:<ul><li>Set <b>resource</b> parameter to <b>indicators</b></li><li>The <b>query</b> parameter should be set to <b>{ "c-value": "baddomain.com" }</b></li></ul>To add more values to match just add the required key-value pairs to the <b>query</b> dictionary.<br>While orchestrating this action from the UI, typing the JSON dictionary should suffice.<br>While automating this action from a playbook, if you are creating a dictionary, then you will require to convert it into a JSON string using the json.loads(...) python function before passing it as the value to the <b>query</b> parameter.<br>If the next page URI is present, the other parameters will be ignored. If it isn't present, the resource to query on the field must be present.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**resource** | optional | Resource to query on. Required if no Page URI is present | string | `crits resource` |
**query** | optional | Query to run | string | `crits query` |
**limit** | optional | Results per page | numeric | |
**offset** | optional | Paging offset | numeric | |
**next_page** | optional | Next page URI | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.resource | string | `crits resource` | |
action_result.parameter.query | string | `crits query` | |
action_result.parameter.limit | numeric | | |
action_result.parameter.offset | numeric | | |
action_result.parameter.next_page | string | | |
action_result.data.\*.\_id | string | `crits resource id` | |
action_result.data.\*.activity.\*.analyst | string | | |
action_result.data.\*.activity.\*.date | string | | |
action_result.data.\*.activity.\*.description | string | | |
action_result.data.\*.activity.\*.end_date | string | | |
action_result.data.\*.activity.\*.start_date | string | | |
action_result.data.\*.attack_types | string | | |
action_result.data.\*.campaign.\*.analyst | string | | |
action_result.data.\*.campaign.\*.confidence | string | | |
action_result.data.\*.campaign.\*.date | string | | |
action_result.data.\*.campaign.\*.description | string | | |
action_result.data.\*.campaign.\*.name | string | | |
action_result.data.\*.confidence.analyst | string | | |
action_result.data.\*.confidence.rating | string | | |
action_result.data.\*.created | string | | |
action_result.data.\*.description | string | | |
action_result.data.\*.impact.analyst | string | | |
action_result.data.\*.impact.rating | string | | |
action_result.data.\*.lower | string | | |
action_result.data.\*.modified | string | | |
action_result.data.\*.relationships.\*.analyst | string | | |
action_result.data.\*.relationships.\*.date | string | | |
action_result.data.\*.relationships.\*.rel_confidence | string | | |
action_result.data.\*.relationships.\*.rel_reason | string | | |
action_result.data.\*.relationships.\*.relationship | string | | |
action_result.data.\*.relationships.\*.relationship_date | string | | |
action_result.data.\*.relationships.\*.type | string | | |
action_result.data.\*.relationships.\*.value | string | | |
action_result.data.\*.schema_version | numeric | | |
action_result.data.\*.source.\*.instances.\*.analyst | string | | |
action_result.data.\*.source.\*.instances.\*.date | string | | |
action_result.data.\*.source.\*.instances.\*.method | string | | |
action_result.data.\*.source.\*.instances.\*.reference | string | | |
action_result.data.\*.source.\*.name | string | | |
action_result.data.\*.status | string | | |
action_result.data.\*.threat_types | string | | |
action_result.data.\*.type | string | `crits resource` | |
action_result.data.\*.value | string | | |
action_result.data.\*.domain | string | | |
action_result.data.\*.analyst | string | | |
action_result.data.\*.watchlistEnabled | boolean | | True False |
action_result.summary.total_results | numeric | | |
action_result.summary.next_page | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'get resource'

Get a specific resource from CRITs

Type: **investigate** <br>
Read only: **True**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** | required | Resource ID to get | string | `crits resource id` |
**resource** | required | Resource to get | string | `crits resource` |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.id | string | `crits resource id` | |
action_result.parameter.resource | string | `crits resource` | |
action_result.data.\*.\_id | string | `crits resource id` | |
action_result.data.\*.created | string | | |
action_result.data.\*.activity.\*.analyst | string | | |
action_result.data.\*.activity.\*.date | string | | |
action_result.data.\*.activity.\*.description | string | | |
action_result.data.\*.activity.\*.end_date | string | | |
action_result.data.\*.activity.\*.start_date | string | | |
action_result.data.\*.attack_types | string | | |
action_result.data.\*.campaign.\*.analyst | string | | |
action_result.data.\*.campaign.\*.confidence | string | | |
action_result.data.\*.campaign.\*.date | string | | |
action_result.data.\*.campaign.\*.description | string | | |
action_result.data.\*.campaign.\*.name | string | | |
action_result.data.\*.confidence.analyst | string | | |
action_result.data.\*.confidence.rating | string | | |
action_result.data.\*.description | string | | |
action_result.data.\*.filedata | string | | |
action_result.data.\*.filename | string | | |
action_result.data.\*.filetype | string | | |
action_result.data.\*.impact.analyst | string | | |
action_result.data.\*.impact.rating | string | | |
action_result.data.\*.lower | string | | |
action_result.data.\*.md5 | string | | |
action_result.data.\*.mimetype | string | | |
action_result.data.\*.modified | string | | |
action_result.data.\*.name | string | | |
action_result.data.\*.relationships.\*.analyst | string | | |
action_result.data.\*.relationships.\*.date | string | | |
action_result.data.\*.relationships.\*.rel_confidence | string | | |
action_result.data.\*.relationships.\*.rel_reason | string | | |
action_result.data.\*.relationships.\*.relationship | string | | |
action_result.data.\*.relationships.\*.relationship_date | string | | |
action_result.data.\*.relationships.\*.type | string | | |
action_result.data.\*.relationships.\*.value | string | | |
action_result.data.\*.schema_version | numeric | | |
action_result.data.\*.sha1 | string | | |
action_result.data.\*.sha256 | string | | |
action_result.data.\*.size | numeric | | |
action_result.data.\*.source.\*.instances.\*.analyst | string | | |
action_result.data.\*.source.\*.instances.\*.date | string | | |
action_result.data.\*.source.\*.instances.\*.method | string | | |
action_result.data.\*.source.\*.instances.\*.reference | string | | |
action_result.data.\*.source.\*.name | string | | |
action_result.data.\*.ssdeep | string | | |
action_result.data.\*.status | string | | |
action_result.data.\*.threat_types | string | | |
action_result.data.\*.type | string | | |
action_result.data.\*.value | string | | |
action_result.summary.resource_id | string | `crits resource id` | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'update resource'

Update a specified resource

Type: **generic** <br>
Read only: **False**

The <b>patch_data</b> field expects a json string that will be accepted by the action handler. More information can be found at <a href="https://github.com/crits/crits/wiki/Authenticated-API">this link</a>, in the sections about updating TLOs using PATCH.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** | required | Resource ID to update | string | `crits resource id` |
**resource** | required | Resource type to update | string | `crits resource` |
**patch_data** | required | Update JSON Data | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.id | string | `crits resource id` | |
action_result.parameter.resource | string | `crits resource` | |
action_result.parameter.patch_data | string | | |
action_result.data.\*.id | string | `crits resource id` | |
action_result.data.\*.message | string | | |
action_result.data.\*.return_code | numeric | | |
action_result.data.\*.type | string | `crits resource` | |
action_result.summary.resource_id | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'create resource'

Create a resource

Type: **generic** <br>
Read only: **False**

All resources expect different fields, save a few common fields. The <b>post_data</b> field expects a json string. More information can be found at <a href="https://github.com/crits/crits/wiki/Authenticated-API">this link</a>. Each resource has a section outlining its specific fields.</br>If no confidence is specified, it will default to "low".<br> Additionally, you can upload files through the vault to be added to the resource. However, not all resource types will accept a file. If you attempt to add a file to a resource that doesn't accept one, then the action will still succeed and a resource will be created, but the attachment will not be added to it. By default, each file will be added as a 'raw' file. If you wish to change this, for example, to upload a zip file, you can set the 'file_format' attribute in the <b>post_data</b> to 'zip'.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**resource** | required | New Resource Type | string | `crits resource` |
**vault_id** | optional | File to add to resource | string | `vault id` |
**source** | required | The Source of the resource | string | |
**confidence** | optional | Confidence | string | |
**post_data** | optional | Post JSON Data | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.resource | string | `crits resource` | |
action_result.parameter.vault_id | string | `vault id` | |
action_result.parameter.source | string | | |
action_result.parameter.confidence | string | | |
action_result.parameter.post_data | string | | |
action_result.data.\*.id | string | `crits resource id` | |
action_result.data.\*.message | string | | |
action_result.data.\*.return_code | numeric | | |
action_result.data.\*.type | string | `crits resource` | |
action_result.data.\*.url | string | | |
action_result.summary.resource_id | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

______________________________________________________________________

Auto-generated Splunk SOAR Connector documentation.

Copyright 2026 Splunk Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
