import asyncio
from fastmcp import Client

client = Client("server.py")

async def call_list_prs_tool(repo: str):
    async with client:
        result = await client.call_tool("list_prs", {"repo": repo})
        print(result)

asyncio.run(call_list_prs_tool("cymake/closerx"))