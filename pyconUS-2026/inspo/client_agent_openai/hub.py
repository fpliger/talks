"""Access to Hub services."""


from pyscript_cloud.http import http_get, http_post
from pyscript_cloud.secrets import get_secret

from hub_assistant import Assistant, tool
from hub_collections import Collections


class Hub:
    def __init__(self, hub_api_key, assist_api_url, acdc_api_url, collections_api_url, use_mcp_tools=False):
        self.assistant = Assistant(hub_api_key, assist_api_url, acdc_api_url, use_mcp_tools=use_mcp_tools)
        self.collections = Collections(hub_api_key, collections_api_url)
        Hub.instance = self