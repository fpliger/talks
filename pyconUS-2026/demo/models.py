"""Thin compatibility shim — main logic lives in tiers.py.

Kept so send_message() in main.py can still call browser/local/remote
generate without knowing about tier objects.
"""

from tiers import InBrowserTier, LocalTier, RemoteTier, _init_browser_engine


async def init_browser_model():
    return await _init_browser_engine()


async def browser_stream(messages: list):
    async for delta in InBrowserTier().stream_chat(messages):
        yield delta


async def local_stream(messages: list, tools=None):
    async for delta in LocalTier().stream_chat(messages, tools):
        yield delta


async def remote_stream(messages: list, tools=None):
    async for delta in RemoteTier().stream_chat(messages, tools):
        yield delta
