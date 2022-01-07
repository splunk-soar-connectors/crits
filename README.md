[comment]: # "Auto-generated SOAR connector documentation"
# CRITs

Publisher: Splunk  
Connector Version: 2\.0\.4  
Product Vendor: MITRE  
Product Name: CRITs  
Product Version Supported (regex): "\.\*"  
Minimum Product Version: 4\.9\.39220  

This App supports various investigative actions on CRITs

### Configuration Variables
The below configuration variables are required for this Connector to operate.  These variables are specified when configuring a CRITs asset in SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**url** |  required  | string | Device URL e\.g\. https\://mycrits\.contoso\.com\:8080
**verify\_server\_cert** |  optional  | boolean | Verify server certificate
**username** |  required  | string | Username
**api\_key** |  required  | password | API Key

### Supported Actions  
[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity\. This action logs into the device to check the connection and credentials  
[run query](#action-run-query) - Run a search query on the CRITs device  
[get resource](#action-get-resource) - Get a specific resource from CRITs  
[update resource](#action-update-resource) - Update a specified resource  
[create resource](#action-create-resource) - Create a resource  

## action: 'test connectivity'
Validate the asset configuration for connectivity\. This action logs into the device to check the connection and credentials

Type: **test**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
No Output  

## action: 'run query'
Run a search query on the CRITs device

Type: **investigate**  
Read only: **True**

Query on CRITs is made up of multiple instances of key\-value pairs, much like the parameters that are specified to an HTTP URL\. To keep things simple, the action takes as input each parameter and its value to match as a JSON dictionary \(in string form\)\.<br>For example to search for an indicator of value <b>baddomain\.com</b>\:<ul><li>Set <b>resource</b> parameter to <b>indicators</b></li><li>The <b>query</b> parameter should be set to <b>\{ "c\-value"\: "baddomain\.com" \}</b></li></ul>To add more values to match just add the required key\-value pairs to the <b>query</b> dictionary\.<br>While orchestrating this action from the UI, typing the JSON dictionary should suffice\.<br>While automating this action from a playbook, if you are creating a dictionary, then you will require to convert it into a JSON string using the json\.loads\(\.\.\.\) python function before passing it as the value to the <b>query</b> parameter\.<br>If the next page URI is present, the other parameters will be ignored\. If it isn't present, the resource to query on the field must be present\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**resource** |  optional  | Resource to query on\. Required if no Page URI is present | string |  `crits resource` 
**query** |  optional  | Query to run | string |  `crits query` 
**limit** |  optional  | Results per page | numeric | 
**offset** |  optional  | Paging offset | numeric | 
**next\_page** |  optional  | Next page URI | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.limit | numeric | 
action\_result\.parameter\.next\_page | string | 
action\_result\.parameter\.offset | numeric | 
action\_result\.parameter\.query | string |  `crits query` 
action\_result\.parameter\.resource | string |  `crits resource` 
action\_result\.data\.\*\.\_id | string |  `crits resource id` 
action\_result\.data\.\*\.activity\.\*\.analyst | string | 
action\_result\.data\.\*\.activity\.\*\.date | string | 
action\_result\.data\.\*\.activity\.\*\.description | string | 
action\_result\.data\.\*\.activity\.\*\.end\_date | string | 
action\_result\.data\.\*\.activity\.\*\.start\_date | string | 
action\_result\.data\.\*\.attack\_types | string | 
action\_result\.data\.\*\.campaign\.\*\.analyst | string | 
action\_result\.data\.\*\.campaign\.\*\.confidence | string | 
action\_result\.data\.\*\.campaign\.\*\.date | string | 
action\_result\.data\.\*\.campaign\.\*\.description | string | 
action\_result\.data\.\*\.campaign\.\*\.name | string | 
action\_result\.data\.\*\.confidence\.analyst | string | 
action\_result\.data\.\*\.confidence\.rating | string | 
action\_result\.data\.\*\.created | string | 
action\_result\.data\.\*\.description | string | 
action\_result\.data\.\*\.impact\.analyst | string | 
action\_result\.data\.\*\.impact\.rating | string | 
action\_result\.data\.\*\.lower | string | 
action\_result\.data\.\*\.modified | string | 
action\_result\.data\.\*\.relationships\.\*\.analyst | string | 
action\_result\.data\.\*\.relationships\.\*\.date | string | 
action\_result\.data\.\*\.relationships\.\*\.rel\_confidence | string | 
action\_result\.data\.\*\.relationships\.\*\.rel\_reason | string | 
action\_result\.data\.\*\.relationships\.\*\.relationship | string | 
action\_result\.data\.\*\.relationships\.\*\.relationship\_date | string | 
action\_result\.data\.\*\.relationships\.\*\.type | string | 
action\_result\.data\.\*\.relationships\.\*\.value | string | 
action\_result\.data\.\*\.schema\_version | numeric | 
action\_result\.data\.\*\.source\.\*\.instances\.\*\.analyst | string | 
action\_result\.data\.\*\.source\.\*\.instances\.\*\.date | string | 
action\_result\.data\.\*\.source\.\*\.instances\.\*\.method | string | 
action\_result\.data\.\*\.source\.\*\.instances\.\*\.reference | string | 
action\_result\.data\.\*\.source\.\*\.name | string | 
action\_result\.data\.\*\.status | string | 
action\_result\.data\.\*\.threat\_types | string | 
action\_result\.data\.\*\.type | string |  `crits resource` 
action\_result\.data\.\*\.value | string | 
action\_result\.summary\.total\_results | numeric | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'get resource'
Get a specific resource from CRITs

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** |  required  | Resource ID to get | string |  `crits resource id` 
**resource** |  required  | Resource to get | string |  `crits resource` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.id | string |  `crits resource id` 
action\_result\.parameter\.resource | string |  `crits resource` 
action\_result\.data\.\*\.\_id | string |  `crits resource id` 
action\_result\.data\.\*\.activity\.\*\.analyst | string | 
action\_result\.data\.\*\.activity\.\*\.date | string | 
action\_result\.data\.\*\.activity\.\*\.description | string | 
action\_result\.data\.\*\.activity\.\*\.end\_date | string | 
action\_result\.data\.\*\.activity\.\*\.start\_date | string | 
action\_result\.data\.\*\.attack\_types | string | 
action\_result\.data\.\*\.campaign\.\*\.analyst | string | 
action\_result\.data\.\*\.campaign\.\*\.confidence | string | 
action\_result\.data\.\*\.campaign\.\*\.date | string | 
action\_result\.data\.\*\.campaign\.\*\.description | string | 
action\_result\.data\.\*\.campaign\.\*\.name | string | 
action\_result\.data\.\*\.confidence\.analyst | string | 
action\_result\.data\.\*\.confidence\.rating | string | 
action\_result\.data\.\*\.created | string | 
action\_result\.data\.\*\.description | string | 
action\_result\.data\.\*\.filedata | string | 
action\_result\.data\.\*\.filename | string | 
action\_result\.data\.\*\.filetype | string | 
action\_result\.data\.\*\.impact\.analyst | string | 
action\_result\.data\.\*\.impact\.rating | string | 
action\_result\.data\.\*\.lower | string | 
action\_result\.data\.\*\.md5 | string | 
action\_result\.data\.\*\.mimetype | string | 
action\_result\.data\.\*\.modified | string | 
action\_result\.data\.\*\.name | string | 
action\_result\.data\.\*\.relationships\.\*\.analyst | string | 
action\_result\.data\.\*\.relationships\.\*\.date | string | 
action\_result\.data\.\*\.relationships\.\*\.rel\_confidence | string | 
action\_result\.data\.\*\.relationships\.\*\.rel\_reason | string | 
action\_result\.data\.\*\.relationships\.\*\.relationship | string | 
action\_result\.data\.\*\.relationships\.\*\.relationship\_date | string | 
action\_result\.data\.\*\.relationships\.\*\.type | string | 
action\_result\.data\.\*\.relationships\.\*\.value | string | 
action\_result\.data\.\*\.schema\_version | numeric | 
action\_result\.data\.\*\.sha1 | string | 
action\_result\.data\.\*\.sha256 | string | 
action\_result\.data\.\*\.size | numeric | 
action\_result\.data\.\*\.source\.\*\.instances\.\*\.analyst | string | 
action\_result\.data\.\*\.source\.\*\.instances\.\*\.date | string | 
action\_result\.data\.\*\.source\.\*\.instances\.\*\.method | string | 
action\_result\.data\.\*\.source\.\*\.instances\.\*\.reference | string | 
action\_result\.data\.\*\.source\.\*\.name | string | 
action\_result\.data\.\*\.ssdeep | string | 
action\_result\.data\.\*\.status | string | 
action\_result\.data\.\*\.threat\_types | string | 
action\_result\.data\.\*\.type | string | 
action\_result\.data\.\*\.value | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'update resource'
Update a specified resource

Type: **generic**  
Read only: **False**

The <b>patch\_data</b> field expects a json string that will be accepted by the action handler\. More information can be found at <a href="https\://github\.com/crits/crits/wiki/Authenticated\-API">this link</a>, in the sections about updating TLOs using PATCH\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** |  required  | Resource ID to update | string |  `crits resource id` 
**resource** |  required  | Resource type to update | string |  `crits resource` 
**patch\_data** |  required  | Update JSON Data | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.id | string |  `crits resource id` 
action\_result\.parameter\.patch\_data | string | 
action\_result\.parameter\.resource | string |  `crits resource` 
action\_result\.data\.\*\.id | string |  `crits resource id` 
action\_result\.data\.\*\.message | string | 
action\_result\.data\.\*\.return\_code | numeric | 
action\_result\.data\.\*\.type | string |  `crits resource` 
action\_result\.summary\.resource\_id | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'create resource'
Create a resource

Type: **generic**  
Read only: **False**

All resources expect different fields, save a few common fields\. The <b>post\_data</b> field expects a JSON string\. More information can be found at <a href="https\://github\.com/crits/crits/wiki/Authenticated\-API">this link</a>\. Each resource has a section outlining its specific fields\.</br>If no confidence is specified, it will default to "low"\.<br> Additionally, you can upload files through the vault to be added to the resource\. However, not all resource types will accept a file\. If you attempt to add a file to a resource that doesn't accept one, then the action will still succeed and a resource will be created, but the attachment will not be added to it\. By default, each file will be added as a 'raw' file\. If you wish to change this, for example, to upload a zip file, you can set the 'file\_format' attribute in the <b>post\_data</b> to 'zip'\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**resource** |  required  | New Resource Type | string |  `crits resource` 
**vault\_id** |  optional  | File to add to resource | string |  `vault id` 
**source** |  required  | The Source of the resource | string | 
**confidence** |  optional  | Confidence | string | 
**post\_data** |  optional  | Post JSON Data | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.confidence | string | 
action\_result\.parameter\.post\_data | string | 
action\_result\.parameter\.resource | string |  `crits resource` 
action\_result\.parameter\.source | string | 
action\_result\.parameter\.vault\_id | string |  `vault id` 
action\_result\.data\.\*\.id | string |  `crits resource id` 
action\_result\.data\.\*\.message | string | 
action\_result\.data\.\*\.return\_code | numeric | 
action\_result\.data\.\*\.type | string |  `crits resource` 
action\_result\.data\.\*\.url | string | 
action\_result\.summary\.resource\_id | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric | 