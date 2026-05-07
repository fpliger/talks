"""Example of using both local tools and MCP tools via ACDC."""


from hub import Hub, get_secret, tool


@tool(
    description="Get the smell of a location",
    inputs=[
        dict(name="location", type=str, description="The city and state, e.g. San Francisco, CA")
    ]
)
async def smells_like(location):
    import random
    return {"smell": random.choice(["old socks", "soggy newspapers", "roses", "fish and chips"])}



async def chat_loop(hub):
    """Chat loop with tool usage."""
    
    async def on_message_delta(text):
        print(text, end="", flush=True)

    messages = []
    while True:
        prompt = input(f"┌[°_°]┐ ? ")
        if prompt.strip():
            if prompt.lower() == "quit" or prompt.lower() == "q":
                break

        print()
        
        messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        await hub.assistant.invoke(
            messages=messages,
            on_message_delta=on_message_delta,
            tools=[smells_like]
        )

        print('\n')
        
    print('\nGoodbye!\n')


async def main():
    api_key = await get_secret("hub-api-key", "HUB API Key")
    if api_key:
        hub = Hub(
            #
            # Hub API key.
            #
            hub_api_key=api_key,
            #
            # Allow use of MCP tools?
            #
            use_mcp_tools=False,
            #
            # Service URLs.
            #
            # Assist.
            #
            #assist_api_url="https://pyscript-dev.com/api/assist",
            # assist_api_url="http://localhost:8084/api/assist",
            assist_api_url="https://ccb1b0e8f92c.ngrok-free.app",
            #
            # Anaconda Desktop API (MCP client).
            #
            acdc_api_url="http://localhost:8099/api",
            #
            # Collections.
            #
            collections_api_url="https://stage.anaconda.com/api/projects"
        )
        await chat_loop(hub)
        
    else:
        from pyscript import window
        window.alert("API Key Required")


if __name__ == "__main__":
    await main()
