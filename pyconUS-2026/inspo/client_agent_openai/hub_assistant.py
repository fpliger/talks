"""Assistant Service Client."""


import json

from pyscript import fetch, window

from pyscript_cloud.http import http_get, http_post
from pyscript_cloud.secrets import get_secret
from pyscript_cloud.websockets import ReconnectingWebSocket


# Registered tools.
registered_tools = {}


def create_tool_spec(func, description, inputs):
    """Create a tool definition for OpenAI.
    
    e.g. the output might be something like:

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
        "name": func.__name__,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalParameters": False
        }
    }


def register_tool(func, description, inputs):
    """Register a tool."""

    registered_tools[func.__name__] = create_tool_spec(func, description, inputs)


def tool(description, inputs=None):
    """Decorator for registering a tool."""

    def decorator(func):
        register_tool(func, description, inputs or [])        
        return func
        
    return decorator


class Assistant:
    #ASSIST_API_URL="https://pyscript-dev.com/api/assist/v1/responses"
    #ASSIST_API_URL="http://localhost:8084/api/assist"
    ASSIST_API_URL="https://api.openai.com/v1/responses"

    # Anaconda Desktop.
    ACDC_API_URL="http://localhost:8099/api"

    def __init__(self, hub_api_key, openai_api_key):
        self.hub_api_key = hub_api_key
        self.openai_api_key = openai_api_key

    async def invoke(self, messages, system=None, tools=None, on_message_delta=None):
        """Invoke the assistant."""

        # 'tools' is a list of the actual tool *functions*, here we look up their tool definitions.
        tool_definitions = [registered_tools[tool.__name__] for tool in tools]

        tool_calls = await self._streaming_response(messages, system, tool_definitions, on_message_delta)
        while len(tool_calls) > 0:
            for output_index, tool_call in tool_calls.items():
                messages.append(tool_call)
                messages.append(await self._call_tool(tools, tool_call))

            tool_calls = await self._streaming_response(messages, system, tool_definitions, on_message_delta)

        return messages

    # Internal ##########################################################################################

    async def _streaming_response(self, messages, system, tools, on_message_delta):
        """Call the streaming response endpoint and process the resulting stream.
        
        Returns a (possibly empty) dictionary of required tools calls.
        
        """

        system = system or []
        
        # The conversation so far.
        post_data = {"input": messages, "model": "gpt-4.1", "stream": True}

        # Optional system prompt.
        if system:
            post_data["system"] = system

        # Optional tools.
        if tools:
            post_data["tools"] = tools

        response = await fetch(
            self.ASSIST_API_URL,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.hub_api_key}"
            },
            body=json.dumps(post_data)
        )

        if response.status != 200:
            raise SystemError(f"Error getting response: {response.status}")
            
        tool_calls = {}

        event = ""
        async for chunk in self._generate_events(response):
            if chunk.startswith("event:"):
                event = ""
                
            elif chunk.startswith("data:"):
                event += chunk.removeprefix("data: ")

            else:
                event += chunk

            try:
                event = json.loads(chunk.removeprefix("data: "))

                if event["type"] == "response.output_item.added":
                    if event["item"]["type"] == "function_call":
                        tool_calls[event["output_index"]] = event["item"]
        
                elif event["type"] == "response.function_call_arguments.delta":
                    index = event["output_index"]
        
                    if tool_calls[index]:
                        tool_calls[index]["arguments"] += event["delta"]
        
                elif event["type"] == "response.output_text.delta":
                    if on_message_delta:
                        await on_message_delta(event["delta"])

                event = ""
                
            except json.JSONDecodeError:
                ...
        
        return tool_calls
            

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

                # Check if we have any complete chunks.
                while '\n' in buffer:
                    # Split at the first newline.
                    chunk, buffer = buffer.split('\n', 1)

                    # Load the JSON and yield the event as a dictionary.
                    yield chunk
                
            except Exception:
                ...
    
        # After the stream ends, yield any remaining data in the buffer.
        if buffer:
            yield json.loads(buffer)
    
    async def _call_tool(self, tools, tool_call):
        """Call a tool."""

        for tool in tools:
            if tool_call["name"] == tool.__name__:
                print(tool_call["arguments"])
                result = await tool(**json.loads(tool_call["arguments"]))
                message = {
                    "type": "function_call_output",
                    "call_id": tool_call["call_id"],
                    "output": json.dumps(result)
                }
                break
                
        else:
            result = await http_post(
                self.ACDC_API_URL +  "/mcp/call-tool", self.api_key,
                {
                    "name": tool_call["name"],
                    "arguments": tool_call["arguments"]
                }
            )

            # This is assuming that we are using the `HTTPMCPClient` as we are expecting
            # dictionaries.
            content = ""
            for item in result["content"]:
                if item["type"] == "text":
                    content += item["text"]

            message = {
                "role": "user",
                "content": [
                    {
                        "toolResult": {
                            "toolUseId": tool_use['toolUseId'],
                            "content": content
                        }
                    }
                ]
            }

        return message
