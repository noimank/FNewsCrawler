
from fnewscrawler.mcp import mcp_server
from fnewscrawler.core.redis_manager import  get_redis
import os

class MCPManager:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    def __init__(self):
        self.mcp_server = mcp_server
        self.redis = get_redis()
        #该环境变量用于区分多实例部署时，每个实例的mcp状态的记忆，方便恢复
        self.deploy_node_name = os.getenv("DEPLOY_NODE_NAME", "FNewsCrawlerNode")
    
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
        :return: 工具信息
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
            #主要针对有些mcp工具定义时就是关闭的，状态改变则需要记录
            self.redis.set(f"fnewscrawler:{self.deploy_node_name}:mcp:status:{tool_name}", True)
            return True
        except Exception as e:
            self.redis.delete(f"fnewscrawler:{self.deploy_node_name}:mcp:status:{tool_name}")
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
            self.redis.set(f"fnewscrawler:{self.deploy_node_name}:mcp:status:{tool_name}", False)
            return True
        except Exception as e:
            self.redis.delete(f"fnewscrawler:{self.deploy_node_name}:mcp:status:{tool_name}")
            return False

    async def init_tools_status(self):
        """
        数据库里面保存着用户修改的mcp工具的信息，需要在启动时恢复这些工具的状态
        :return:
        """
        keys = self.redis.scan_iter(f"fnewscrawler:{self.deploy_node_name}:mcp:status:*")
        for key in keys:
            value = self.redis.get(key)
            # key可能是字符串或字节，需要处理
            if isinstance(key, bytes):
                tool_name = key.decode().split(":")[-1]
            else:
                tool_name = key.split(":")[-1]
            if not value:
                await self.disable_tool(tool_name)
            else:
                await self.enable_tool(tool_name)

    async def call_tool(self, tool_name:str, **kwargs)->dict:
        """
        调用工具
        :param tool_name: 工具名称
        :param kwargs: 工具参数
        :return: 工具返回值，字典格式
        """
        tool = await self.mcp_server.get_tool(tool_name)
        if tool:
            result = await tool.run(kwargs)
            return result.structured_content
            # return result.content
        else:
            return {"error": f"工具{tool_name}不存在"}
