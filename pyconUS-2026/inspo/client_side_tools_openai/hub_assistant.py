"""PSDC Assist Service Client."""


import json

from pyscript import fetch, window

from pyscript_cloud.http import http_get, http_post
from pyscript_cloud.secrets import get_secret


# Tool definitions for all *local* tools (see `create_tool_definitions` below).
#
# { fn.__name__ : dict }
tool_definitions = {}


def create_tool_definition(func, description, inputs):
    """Create a tool definition for the OpenAI `completions` API.
    
    e.g. the output might be something like:

    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current temperature for a given location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City and country e.g. Bogotá, Colombia"
                    }
                },
                "required": [
                    "location"
                ],
                "additionalProperties": False
            }
        }
    }
    
    """

    type_map = {
        str: "string",
        int: "integer",
        list: "array"
    }

    properties = {}; required = []
    for input in inputs:
        input_type = input["type"]
        if type(input_type) is type:
            input_type = type_map[input_type]
            
        properties[input["name"]] = {
            "type": input_type,
            "description": input["description"],
        }

        if input.get("required", True):
            required.append(input["name"])
    
    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalParameters": False
            }
        }
    }


def register_tool(func, description, inputs):
    """Register a tool."""

    tool_definitions[func.__name__] = create_tool_definition(func, description, inputs)


def tool(description, inputs=None):
    """Decorator for registering a tool."""

    def decorator(func):
        register_tool(func, description, inputs or [])        
        return func
        
    return decorator


class Assistant:
    def __init__(self, hub_api_key, assist_api_url, acdc_api_url, use_mcp_tools=False):
        self.hub_api_key = hub_api_key
        self.assist_api_url = assist_api_url
        self.acdc_api_url = acdc_api_url
        self.use_mcp_tools = use_mcp_tools

    async def invoke(self, messages, tools=None, on_message_delta=None):
        """Invoke the assistant."""

        # Optional local tools (i.e. tool functions that are defined in this project)..
        #
        # 'tools' is a list of the actual tool *functions*, here we look up their tool definitions.
        tool_definitions = self._create_local_tool_definitions(tools)

        # MCP tools defined in ACDC.
        if self.use_mcp_tools:
            mcp_tool_definitions = await self._list_mcp_tools()
            if mcp_tool_definitions:
                tool_definitions.extend(self._create_mcp_tool_definitions(mcp_tool_definitions))

        message, tool_calls = await self._completions_stream(messages, tool_definitions, on_message_delta)
        while len(tool_calls) > 0:
            # In the `completions` API we just add one assistant message for all of the tools calls
            # requested (i.e. not, one message per tool call).
            messages.append({"role": "assistant", "tool_calls": list(tool_calls.values())})
            for output_index, tool_call in tool_calls.items():
                messages.append(await self._call_tool(tools, tool_call))

            message, tool_calls = await self._completions_stream(messages, tool_definitions, on_message_delta)

        return messages

    # Internal ##########################################################################################

    def _create_local_tool_definitions(self, tools):
        """Create tool specs for any local tools."""

        return [tool_definitions[tool.__name__] for tool in tools]

    def _create_mcp_tool_definitions(self, mcp_tools):
        """Create the tools for the specified MCP tools in OpenAI `responses` format.
    
        Args:
            mcp_tools: List of MCP tools.
    
            e.g.
    
            [
                Tool(
                    name='list_projects',
                    description='List my projects on pyscript.com (aka PSDC).',
                    inputSchema={
                    'properties': {}, 'title': 'list_projectsArguments', 'type':'object'
                    }
                )
            ]
    
        Returns:
            List of tool specifications.
    
            e.g.
    
            [
                {
                    "type": "function",
                    "name": "get_weather",
                    "description": "Get current temperature for a given location.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "City and country e.g. Bogotá, Colombia"
                            }
                        },
                        "required": [
                            "location"
                        ],
                        "additionalProperties": False
                    }
                }
            ]
    
        """
    
        tools = []
        for mcp_tool in mcp_tools:
            # This allows us to use this function when using both a local MCP client
            # and an HTTP MCP client.
            if not isinstance(mcp_tool, dict):
                mcp_tool = mcp_tool.model_dump()
    
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": mcp_tool["name"],
                        "description": mcp_tool["description"],
                        "parameters": {
                            "type": "object",
                            "properties": mcp_tool["inputSchema"].get("properties", {}),
                            "required": mcp_tool["inputSchema"].get("required", []),
                            "additionalProperties": False
                        }
                    }
                }
            )
    
        return tools

    async def _completions_stream(self, messages, tools, on_message_delta):
        """Call the OpenAI-compatible `v1/chat/completions` endpoint on the assist service.
        
        Returns an (optional) message from the assistant along with a (possibly empty) dictionary 
        of required tools calls.
        
        """

        post_data = {"messages": messages, "stream": True, "model": "Fred"}

        if tools:
            post_data["tools"] = tools
            
        response = await fetch(
            self.assist_api_url + "/v1/chat/completions",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.hub_api_key}"
            },
            body=json.dumps(post_data)
        )
        if response.status != 200:
            raise SystemError(f"Error getting response: {response.status}")
            
        text=""; tool_calls = {}
        async for event in self._generate_events(response):
            if "error" in event:
                return {
                    "role": "assistant",
                    "content": event["message"]
                }, {}
    
            delta = event["choices"][0]["delta"]
    
            # The final event has no delta.
            if not delta:
                continue
    
            if event["choices"][0]["finish_reason"] == "stop":
                # print()
                # print(event["x_groq"])
                continue
    
            # We use get here as the last event doesn't have this... clean this up!
            if delta.get("tool_calls"):
                for tool_call_delta in delta["tool_calls"]:
                    index = tool_call_delta["index"]
                    if index not in tool_calls:
                        tool_calls[index] = tool_call_delta
    
                    else:
                        tool_call = tool_calls[index]
                        tool_call["function"]["arguments"] += tool_call_delta["function"]["arguments"]
    
            elif "content" in delta and delta["content"]:
                text += delta["content"]
                if on_message_delta:
                    await on_message_delta(delta["content"])
    
        message = {
            "role": "assistant",
            "content": text
        } if text else None
    
        return message, tool_calls   

    async def _generate_events(self, response):
        """Generate the OpenAI events in the stream."""

        # Create a buffer to hold incomplete chunks.
        buffer = ""

        decoder = window.TextDecoder.new()
        reader = response.body.getReader()

        while True:
            result = await reader.read()
            if result.done:
                break

            try:
                text = decoder.decode(result.value)

                # Add the new data to our buffer.
                buffer += text

                # Check if we have any complete events (each event is separated by a newline).
                while '\n' in buffer:
                    # Split at the first newline.
                    line, buffer = buffer.split('\n', 1)

                    # Remove the "data: " prefix.
                    if line.startswith("data: "):
                        line = line[6:]

                    # Check for the end of the stream.
                    if line == "[DONE]":
                        break

                    try:
                        event = json.loads(line)
                        yield event
        
                    except json.JSONDecodeError:
                        continue                    
                
            except Exception:
                ...
    
    async def _list_mcp_tools(self):
        """List all MCP tools available in ACDC."""

        return await http_get(self.acdc_api_url +  "/mcp/tools", self.hub_api_key)

    async def _call_tool(self, tools, tool_call):
        """Call a tool."""

        tool_name = tool_call["function"]["name"]
        tool_arguments = json.loads(tool_call["function"]["arguments"])

        # Is the tool a local function?
        for tool in tools:
            if tool_name == tool.__name__:
                result = await tool(**tool_arguments)
                message = {
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(result)
                }
                break

        # Otherwise, it must be an MCP tool.
        else:
            result = await http_post(
                self.acdc_api_url +  "/mcp/call-tool", self.hub_api_key,
                {
                    "name": tool_name,
                    "arguments": tool_arguments
                }
            )

            # This is assuming that we are using the `HTTPMCPClient` as we are expecting
            # dictionaries.
            content = ""
            for item in result["content"]:
                if item["type"] == "text":
                    content += item["text"]

            message = {
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": content
            }

        return message
