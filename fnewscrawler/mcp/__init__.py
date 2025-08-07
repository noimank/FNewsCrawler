from fastmcp import FastMCP
mcp_server = FastMCP("FNewsCrawler")
from .mcp_manager import MCPManager

#将子包下的mcp工具更新进来
import fnewscrawler.mcp.iwencai
import fnewscrawler.mcp.common
import fnewscrawler.mcp.eastmoney


__all__ = [
    "mcp_server",
    "MCPManager"
]