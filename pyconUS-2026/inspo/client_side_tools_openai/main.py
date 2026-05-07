"""Example of of using OpenAI with client-side tools."""


from hub import Hub, get_secret
import tools


async def on_message_delta(text):
    print(text, end="", flush=True)


async def chat_loop(hub):
    """Chat with the overlords."""

    messages = []
    while True:
        prompt = input(f'<(•_•)> ')
        if prompt == "bye":
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
            tools=[
                tools.smells_like,
                tools.list_collections,
                tools.check_if_collection_exists,
                tools.create_collection,
                tools.add_file_to_collection,
                tools.get_collection_permissions,
            ],
        )

        print('\n')
        
    print('\nBye!')


if __name__ == "__main__":
    hub_api_key = await get_secret("hub-api-key", "HUB API Key")
    openai_api_key = await get_secret("openai-api-key", "OpenAI API Key")
    
    if hub_api_key and openai_api_key:
        await chat_loop(Hub(hub_api_key, openai_api_key))
        
    else:
        from pyscript import window
        window.alert("Hub and OpenAI API Keys Required")
