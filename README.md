# CRITs

Publisher: Splunk \
Connector Version: 2.1.4 \
Product Vendor: MITRE \
Product Name: CRITs \
Minimum Product Version: 5.1.0

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

[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity. This action logs into the device to check the connection and credentials \
[run query](#action-run-query) - Run a search query on the CRITs device \
[get resource](#action-get-resource) - Get a specific resource from CRITs \
[update resource](#action-update-resource) - Update a specified resource \
[create resource](#action-create-resource) - Create a resource

## action: 'test connectivity'

Validate the asset configuration for connectivity. This action logs into the device to check the connection and credentials

Type: **test** \
Read only: **True**

#### Action Parameters

No parameters are required for this action

#### Action Output

No Output

## action: 'run query'

Run a search query on the CRITs device

Type: **investigate** \
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
action_result.status | string | | success failed |
action_result.parameter.limit | numeric | | 10 100 |
action_result.parameter.next_page | string | | /api/v1/indicators/?limit=1&offset=1 /api/v1/indicators/?limit=1&offset=2 |
action_result.parameter.offset | numeric | | 0 5 |
action_result.parameter.query | string | `crits query` | {"c-value": "www.indicator.com"} |
action_result.parameter.resource | string | `crits resource` | certificates indicators ips |
action_result.data.\*.\_id | string | `crits resource id` | |
action_result.data.\*.activity.\*.analyst | string | | admin |
action_result.data.\*.activity.\*.date | string | | 2017-06-23 17:46:36.544000 |
action_result.data.\*.activity.\*.description | string | | Metal Claws |
action_result.data.\*.activity.\*.end_date | string | | 2017-06-23 17:46:36.544000 |
action_result.data.\*.activity.\*.start_date | string | | 2017-06-23 17:46:36.544000 |
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
action_result.data.\*.domain | string | | mobilalibey.com |
action_result.data.\*.analyst | string | | scott |
action_result.data.\*.watchlistEnabled | boolean | | True False |
action_result.summary.next_page | string | | /api/v1/indicators/?username=admin&api_key=\<api_key>&limit=1&offset=2 |
action_result.summary.total_results | numeric | | 2 |
action_result.message | string | | Total results: 4, Next page: /api/v1/indicators/?username=admin&api_key=\<api_key>&limit=1&offset=1 |
summary.total_objects | numeric | | 2 |
summary.total_objects_successful | numeric | | 2 |

## action: 'get resource'

Get a specific resource from CRITs

Type: **investigate** \
Read only: **True**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** | required | Resource ID to get | string | `crits resource id` |
**resource** | required | Resource to get | string | `crits resource` |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.data.\*.\_id | string | `crits resource id` | |
action_result.status | string | | success failed |
action_result.data.\*.created | string | | |
action_result.parameter.id | string | `crits resource id` | 60ba1a3de1c1dc5cf532dae7 60ba3fh6e1c1dc5cttttdae7 |
action_result.parameter.resource | string | `crits resource` | indicators ips |
action_result.data.\*.activity.\*.analyst | string | | admin |
action_result.data.\*.activity.\*.date | string | | 2017-06-23 17:46:36.544000 |
action_result.data.\*.activity.\*.description | string | | Metal Claws |
action_result.data.\*.activity.\*.end_date | string | | 2017-06-23 17:46:36.544000 |
action_result.data.\*.activity.\*.start_date | string | | 2017-06-23 17:46:36.544000 |
action_result.data.\*.attack_types | string | | |
action_result.data.\*.campaign.\*.analyst | string | | |
action_result.data.\*.campaign.\*.confidence | string | | |
action_result.data.\*.campaign.\*.date | string | | |
action_result.data.\*.campaign.\*.description | string | | |
action_result.data.\*.campaign.\*.name | string | | |
action_result.data.\*.confidence.analyst | string | | |
action_result.data.\*.confidence.rating | string | | |
action_result.data.\*.description | string | | |
action_result.data.\*.filedata | string | | c2FtcGxlIGZpbGUgbGluZTE= |
action_result.data.\*.filename | string | | ph_vault_datafile |
action_result.data.\*.filetype | string | | ASCII text, with no line terminators |
action_result.data.\*.impact.analyst | string | | |
action_result.data.\*.impact.rating | string | | |
action_result.data.\*.lower | string | | |
action_result.data.\*.md5 | string | | testtestcdf080d433600809testtest |
action_result.data.\*.mimetype | string | | text/plain |
action_result.data.\*.modified | string | | |
action_result.data.\*.name | string | | this is me |
action_result.data.\*.relationships.\*.analyst | string | | |
action_result.data.\*.relationships.\*.date | string | | |
action_result.data.\*.relationships.\*.rel_confidence | string | | |
action_result.data.\*.relationships.\*.rel_reason | string | | |
action_result.data.\*.relationships.\*.relationship | string | | |
action_result.data.\*.relationships.\*.relationship_date | string | | |
action_result.data.\*.relationships.\*.type | string | | |
action_result.data.\*.relationships.\*.value | string | | |
action_result.data.\*.schema_version | numeric | | |
action_result.data.\*.sha1 | string | | testteste42e3d5a76a746e07aed942ctesttest |
action_result.data.\*.sha256 | string | | testtestb577f55b302b4485decb454ecf5748c286c745537317ff2etesttest |
action_result.data.\*.size | numeric | | 17 |
action_result.data.\*.source.\*.instances.\*.analyst | string | | |
action_result.data.\*.source.\*.instances.\*.date | string | | |
action_result.data.\*.source.\*.instances.\*.method | string | | |
action_result.data.\*.source.\*.instances.\*.reference | string | | |
action_result.data.\*.source.\*.name | string | | |
action_result.data.\*.ssdeep | string | | 3:MRx:8x |
action_result.data.\*.status | string | | |
action_result.data.\*.threat_types | string | | |
action_result.data.\*.type | string | | |
action_result.data.\*.value | string | | |
action_result.summary | string | | |
action_result.message | string | | Successfully retrieved resource |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'update resource'

Update a specified resource

Type: **generic** \
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
action_result.status | string | | success failed |
action_result.parameter.id | string | `crits resource id` | 594813dee1c1dc600ae36138 |
action_result.parameter.patch_data | string | | {"action": "activity_add", "activity": {"analyst": "admin", "start_date": "2017-06-23 17:46:36.544590", "end_date": "2017-06-23 17:46:36.544590", "description": "Metal Claws", "date": "2017-06-23 17:46:36.544590"}} |
action_result.parameter.resource | string | `crits resource` | indicators ips |
action_result.data.\*.id | string | `crits resource id` | 594813dee1c1dc600ae36138 |
action_result.data.\*.message | string | | success |
action_result.data.\*.return_code | numeric | | 0 |
action_result.data.\*.type | string | `crits resource` | Indicator |
action_result.summary.resource_id | string | | aaaa1a3de1c1dc5cf532deee |
action_result.message | string | | Successfully updated resource |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'create resource'

Create a resource

Type: **generic** \
Read only: **False**

All resources expect different fields, save a few common fields. The <b>post_data</b> field expects a JSON string. More information can be found at <a href="https://github.com/crits/crits/wiki/Authenticated-API">this link</a>. Each resource has a section outlining its specific fields.</br>If no confidence is specified, it will default to "low".<br> Additionally, you can upload files through the vault to be added to the resource. However, not all resource types will accept a file. If you attempt to add a file to a resource that doesn't accept one, then the action will still succeed and a resource will be created, but the attachment will not be added to it. By default, each file will be added as a 'raw' file. If you wish to change this, for example, to upload a zip file, you can set the 'file_format' attribute in the <b>post_data</b> to 'zip'.

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
action_result.status | string | | success failed |
action_result.parameter.confidence | string | | low medium high |
action_result.parameter.post_data | string | | {"event_type": "Sniffing", "title": "Title", "description": "Desciption"} |
action_result.parameter.resource | string | `crits resource` | events |
action_result.parameter.source | string | | Test Source |
action_result.parameter.vault_id | string | `vault id` | 24468a2721dec748cea9373f3e1710ac2cb13237 |
action_result.data.\*.id | string | `crits resource id` | 594d8e29e1c1dc600ae36164 |
action_result.data.\*.message | string | | Success! |
action_result.data.\*.return_code | numeric | | 0 |
action_result.data.\*.type | string | `crits resource` | Event |
action_result.data.\*.url | string | | /api/v1/events/594d8e29e1c1dc600ae36164/ |
action_result.summary.resource_id | string | | aaaa1a3de1c1dc5cf532deee |
action_result.message | string | | Successfully created new resource |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

______________________________________________________________________

Auto-generated Splunk SOAR Connector documentation.

Copyright 2025 Splunk Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
