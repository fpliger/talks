"""Access to Hub services."""


from pyscript_cloud.http import http_get, http_post
from pyscript_cloud.secrets import get_secret

from hub_assistant import Assistant, tool
from hub_collections import Collections


class Hub:
    def __init__(self, hub_api_key, openai_api_key):
        self.assistant = Assistant(hub_api_key, openai_api_key)
        self.collections = Collections(hub_api_key)
        Hub.instance = self