
from fnewscrawler.mcp import mcp_server
from fnewscrawler.core.redis_manager import  get_redis


class MCPManager:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    def __init__(self):
        self.mcp_server = mcp_server
        self.redis = get_redis()
    
    async def get_all_tools_info(self)->list:
        """
        获取所有工具
        :return: 工具列表，每个工具包含名称、描述、状态、标题
        """
        tools_list = []
        tools = await self.mcp_server.get_tools()
        for tool_key, tool_obj in tools.items():
            tools_list.append(
                {
                   "name": tool_obj.name,
                   "description" : tool_obj.description,
                    "enabled": tool_obj.enabled,
                    "title": tool_obj.title
                }
            )
        return tools_list
    
    async def get_tool_info(self, tool_name:str):
        """
        获取工具
        :param tool_name: 工具名称
        :return: 工具对象
        """
        tool = await self.mcp_server.get_tool(tool_name)
        info_dict = {
            "name": tool.name,
            "description": tool.description,
            "enabled": tool.enabled,
            "title": tool.title
        }
        return info_dict
    

    async def get_tool_status(self, tool_name:str)->bool:
        """
        获取工具状态
        :param tool_name: 工具名称
        :return: True为启用，False为禁用    
        """
        tool = await self.get_tool_info(tool_name)
        return tool.get("enabled")
    
    async def enable_tool(self, tool_name:str)->bool:
        """
        启用工具
        :param tool_name: 工具名称
        :return: 启用成功返回True，失败返回False
        """
        try:
            tool = await self.mcp_server.get_tool(tool_name)
            tool.enable()
            self.redis.delete(f"fnewscrawler:mcp:status:{tool_name}")
            return True
        except Exception as e:
            return False
    
    async def disable_tool(self, tool_name:str)->bool:
        """
        禁用工具
        :param tool_name: 工具名称
        :return: 禁用成功返回True，失败返回False
        """
        try:
            tool = await self.mcp_server.get_tool(tool_name)
            tool.disable()
            self.redis.set(f"fnewscrawler:mcp:status:{tool_name}", False)
            return True
        except Exception as e:
            self.redis.delete(f"fnewscrawler:mcp:status:{tool_name}")
            return False

    async def init_tools_status(self):
        """
        数据库里面保存着标记为关闭的工具信息
        """
        keys = self.redis.scan_iter("fnewscrawler:mcp:status:*")
        for key in keys:
            value = await self.redis.get(key)
            #恢复已经禁用的mcp工具状态
            if not value:
                await self.disable_tool(key)
