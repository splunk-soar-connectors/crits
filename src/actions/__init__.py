from soar_sdk.app import App

from .create_resource import (
    CreateResourceOutput,
    CreateResourceParams,
    CreateResourceSummary,
    create_resource,
)
from .get_resource import GetResourceOutput, GetResourceParams, get_resource
from .run_query import RunQueryOutput, RunQueryParams, RunQuerySummary, run_query
from .update_resource import (
    UpdateResourceOutput,
    UpdateResourceParams,
    UpdateResourceSummary,
    update_resource,
)


def register_actions(app: App) -> App:
    app.register_action(
        action=run_query,
        name="run query",
        identifier="run_query",
        description="Run a search query on the CRITs device",
        verbose="""Query on CRITs is made up of multiple instances of key-value pairs, much like the parameters that are specified to an HTTP URL. To keep things simple, the action takes as input each parameter and its value to match as a JSON dictionary (in string form).<br>For example to search for an indicator of value <b>baddomain.com</b>:<ul><li>Set <b>resource</b> parameter to <b>indicators</b></li><li>The <b>query</b> parameter should be set to <b>{ "c-value": "baddomain.com" }</b></li></ul>To add more values to match just add the required key-value pairs to the <b>query</b> dictionary.<br>While orchestrating this action from the UI, typing the JSON dictionary should suffice.<br>While automating this action from a playbook, if you are creating a dictionary, then you will require to convert it into a JSON string using the json.loads(...) python function before passing it as the value to the <b>query</b> parameter.<br>If the next page URI is present, the other parameters will be ignored. If it isn't present, the resource to query on the field must be present.""",
        action_type="investigate",
        read_only=True,
        params_class=RunQueryParams,
        output_class=RunQueryOutput,
        summary_type=RunQuerySummary,
    )
    app.register_action(
        action=get_resource,
        name="get resource",
        identifier="get_resource",
        description="Get a specific resource from CRITs",
        action_type="investigate",
        read_only=True,
        params_class=GetResourceParams,
        output_class=GetResourceOutput,
    )
    app.register_action(
        action=update_resource,
        name="update resource",
        identifier="update_resource",
        description="Update a specified resource",
        verbose="""The <b>patch_data</b> field expects a json string that will be accepted by the action handler. More information can be found at <a href="https://github.com/crits/crits/wiki/Authenticated-API">this link</a>, in the sections about updating TLOs using PATCH.""",
        action_type="generic",
        read_only=False,
        params_class=UpdateResourceParams,
        output_class=UpdateResourceOutput,
        summary_type=UpdateResourceSummary,
    )
    app.register_action(
        action=create_resource,
        name="create resource",
        identifier="create_resource",
        description="Create a resource",
        verbose="""All resources expect different fields, save a few common fields. The <b>post_data</b> field expects a json string. More information can be found at <a href="https://github.com/crits/crits/wiki/Authenticated-API">this link</a>. Each resource has a section outlining its specific fields.</br>If no confidence is specified, it will default to "low".<br> Additionally, you can upload files through the vault to be added to the resource. However, not all resource types will accept a file. If you attempt to add a file to a resource that doesn't accept one, then the action will still succeed and a resource will be created, but the attachment will not be added to it. By default, each file will be added as a 'raw' file. If you wish to change this, for example, to upload a zip file, you can set the 'file_format' attribute in the <b>post_data</b> to 'zip'.""",
        action_type="generic",
        read_only=False,
        params_class=CreateResourceParams,
        output_class=CreateResourceOutput,
        summary_type=CreateResourceSummary,
    )
    return app
