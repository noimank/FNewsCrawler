import asyncio

from fnewscrawler.mcp.mcp_manager import MCPManager



async def test_mcp_manager():
    mcp_manager = MCPManager()
    tools = await mcp_manager.get_all_tools_info()
    print(tools)
    tool = await mcp_manager.disable_tool("iwencai_news_query")
    print(tool)
    statue = await mcp_manager.get_tool_status("iwencai_news_query")
    print(statue)
    # mcp_manager.enable_tool("test_tool")
    # tools = mcp_manager.list_all_tools()
    # print(tools)
    # mcp_manager.disable_tool("test_tool")
    # tools = mcp_manager.list_all_tools()
    # print(tools)




if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(test_mcp_manager())
    loop.close()


