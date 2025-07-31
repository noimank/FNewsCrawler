# MCP工具开发指南

## 📖 概述

FNewsCrawler 基于 FastMCP 框架实现 Model Context Protocol (MCP) 服务，为大模型提供标准化的财经数据访问接口。本文档详细介绍了 MCP 工具的开发流程、注册机制和最佳实践。

## 🏗️ MCP架构设计

### 核心组件

```
MCP服务架构
├── 🧠 FastMCP Server (mcp_server)
│   ├── 工具注册管理
│   ├── 请求路由分发
│   ├── 参数验证处理
│   └── 响应格式化
│
├── 🛠️ MCPManager (单例)
│   ├── 工具状态管理
│   ├── 启用/禁用控制
│   ├── Redis状态持久化
│   └── 工具信息查询
│
├── 📦 Tool Modules (按域名组织)
│   ├── iwencai/
│   │   ├── crawl.py     # MCP工具实现
│   │   └── __init__.py  # 工具注册
│   ├── eastmoney/
│   └── 其他站点.../
│
└── 🔌 Auto Registration
    ├── Python导包机制
    ├── 装饰器自动注册
    └── 统一mcp_server实例
```

### 设计原则

1. **统一注册机制**：所有工具通过 `fnewscrawler.mcp.mcp_server` 单例对象注册
2. **域名组织结构**：按目标网站域名划分工具模块，保持代码组织清晰
3. **自动发现机制**：利用Python导包机制实现工具的自动注册
4. **状态持久化**：工具启用/禁用状态保存到Redis，支持动态管理
5. **标准化接口**：遵循MCP协议规范，确保与各种AI客户端兼容

## 🧩 核心组件详解

### 1. mcp_server - MCP服务实例

**位置**: `fnewscrawler/mcp/__init__.py`

```python
from fastmcp import FastMCP

# 全局唯一的MCP服务器实例
mcp_server = FastMCP("FNewsCrawler")
```

**特点**:
- 全局单例，确保所有工具注册到同一服务实例
- 基于FastMCP框架，提供标准MCP协议支持
- 自动处理工具发现、参数验证和响应格式化

### 2. MCPManager - 工具管理器

**位置**: `fnewscrawler/mcp/mcp_manager.py`

**核心功能**:
```python
class MCPManager:
    async def get_all_tools_info(self) -> list:
        """获取所有工具信息"""
    
    async def get_tool_info(self, tool_name: str):
        """获取单个工具信息"""
    
    async def enable_tool(self, tool_name: str) -> bool:
        """启用工具"""
    
    async def disable_tool(self, tool_name: str) -> bool:
        """禁用工具"""
    
    async def get_tool_status(self, tool_name: str) -> bool:
        """获取工具状态"""
```

## 📁 目录结构规范

### MCP工具模块组织

```
fnewscrawler/mcp/
├── __init__.py                 # MCP服务器实例和管理器
├── mcp_manager.py             # 工具管理器实现
├── iwencai/                   # 同花顺问财工具
│   ├── __init__.py           # 工具注册入口
│   ├── crawl.py              # 爬虫相关工具
│   └── analysis.py           # 分析相关工具（可选）
├── eastmoney/                 # 东方财富工具
│   ├── __init__.py
│   ├── crawl.py
│   └── market.py
└── 新站点/                    # 新增站点工具
    ├── __init__.py
    ├── crawl.py
    └── 其他功能.py
```

### 文件命名规范

- **__init__.py**: 工具注册入口，导入具体工具模块
- **crawl.py**: 数据爬取相关的MCP工具
- **analysis.py**: 数据分析相关的MCP工具
- **market.py**: 市场数据相关的MCP工具
- **其他功能.py**: 根据实际需要命名的功能模块

## 🛠️ 开发实践

### 1. 创建新的MCP工具模块

**步骤1: 创建目录结构**
```bash
mkdir fnewscrawler/mcp/新站点名
touch fnewscrawler/mcp/新站点名/__init__.py
touch fnewscrawler/mcp/新站点名/crawl.py
```

**步骤2: 实现MCP工具**
```python
# fnewscrawler/mcp/新站点名/crawl.py
from fnewscrawler.mcp import mcp_server
from fnewscrawler.spiders.新站点名 import new_site_crawl_from_query
from typing import List, Dict, Any

@mcp_server.tool()
async def new_site_news_query(query: str, page_no: int = 1) -> Dict[str, Any]:
    """
    从新站点获取财经新闻的专业查询工具
    
    这是一个专业的财经资讯查询工具，能够从新站点实时获取最新的财经新闻信息。
    该工具特别适用于股票研究、投资分析和财经市场监控等场景。
    
    主要功能：
    - 实时获取新站点的最新财经资讯
    - 支持股票名称、股票代码、行业关键词等多种查询方式
    - 按时间倒序返回最相关的财经新闻
    - 分页查询支持，提高查询效率
    
    适用场景：
    - 股票基本面分析和研调
    - 行业动态追踪和政策解读
    - 投资决策支持和风险评估
    - 财经事件监控和市场热点分析
    
    Args:
        query (str): 查询关键词，支持以下类型：
            - 股票名称：如"贵州茅台"、"比亚迪"、"腾讯控股"
            - 股票代码：如"600519"、"002594"、"00700"
            - 行业关键词：如"新能源汽车"、"人工智能"、"半导体"
            - 财经概念：如"降准降息"、"IPO上市"、"并购重组"
            - 宏观经济：如"GDP增长"、"CPI数据"、"外汇储备"
        
        page_no (int, optional): 页码，默认为1。每页返回条数根据站点而定。
            - 建议不超过5页以保持查询效率
            - 页码从1开始，支持正整数
    
    Returns:
        Dict[str, Any]: 包含以下字段的查询结果：
            - success (bool): 查询是否成功
            - data (List[Dict]): 新闻列表，每条新闻包含：
                - title (str): 新闻标题
                - content (str): 新闻内容摘要
                - url (str): 新闻详情链接
                - time (str): 发布时间
                - source (str): 新闻来源媒体
            - total (int): 当前页新闻数量
            - page (int): 当前页码
            - message (str): 状态消息
    
    使用建议：
    1. 对于热门股票，建议查询多页获取全面信息
    2. 使用具体的股票代码可获得更精准的结果
    3. 行业关键词查询适合了解板块整体动态
    4. 建议结合多个关键词进行交叉验证
    
    示例：
        # 查询特定股票
        result = await new_site_news_query("贵州茅台", 1)
        
        # 查询行业动态
        result = await new_site_news_query("新能源汽车", 1)
        
        # 查询宏观经济
        result = await new_site_news_query("央行政策", 1)
    """
    try:
        # 调用爬虫函数获取数据
        news_list = await new_site_crawl_from_query(query, page_no)
        
        # 格式化返回结果
        return {
            "success": True,
            "data": news_list,
            "total": len(news_list),
            "page": page_no,
            "message": f"成功获取 {len(news_list)} 条新闻"
        }
        
    except Exception as e:
        return {
            "success": False,
            "data": [],
            "total": 0,
            "page": page_no,
            "message": f"查询失败: {str(e)}"
        }

@mcp_server.tool()
async def new_site_market_data(symbol: str) -> Dict[str, Any]:
    """
    获取新站点的市场数据
    
    Args:
        symbol (str): 股票代码或名称
    
    Returns:
        Dict[str, Any]: 市场数据结果
    """
    try:
        # 实现市场数据获取逻辑
        # market_data = await get_market_data(symbol)
        
        return {
            "success": True,
            "data": {},  # 实际的市场数据
            "message": "市场数据获取成功"
        }
        
    except Exception as e:
        return {
            "success": False,
            "data": {},
            "message": f"获取市场数据失败: {str(e)}"
        }
```

**步骤3: 配置工具注册**
```python
# fnewscrawler/mcp/新站点名/__init__.py

# 导入工具模块，利用Python导包机制完成工具注册
import fnewscrawler.mcp.新站点名.crawl

# 如有其他工具模块，也在此导入
# import fnewscrawler.mcp.新站点名.analysis
# import fnewscrawler.mcp.新站点名.market
```

**步骤4: 更新主MCP模块**
```python
# fnewscrawler/mcp/__init__.py
from fastmcp import FastMCP
mcp_server = FastMCP("FNewsCrawler")
from .mcp_manager import MCPManager

# 将子包下的mcp工具更新进来
import fnewscrawler.mcp.iwencai
import fnewscrawler.mcp.新站点名  # 添加新站点导入

__all__ = [
    "mcp_server",
    "MCPManager"
]
```

### 2. 工具开发最佳实践

#### 工具命名规范
```python
# 好的命名：站点名_功能_动作
@mcp_server.tool()
async def iwencai_news_query(...):
    pass

@mcp_server.tool()
async def eastmoney_market_data(...):
    pass

@mcp_server.tool()
async def sina_stock_analysis(...):
    pass
```

#### 文档字符串规范
```python
@mcp_server.tool()
async def example_tool(param1: str, param2: int = 1) -> Dict[str, Any]:
    """
    工具的简短描述（一行）
    
    详细的工具描述，包括：
    - 主要功能和用途
    - 适用场景
    - 数据来源说明
    
    Args:
        param1 (str): 参数1的详细说明，包括：
            - 参数的作用和意义
            - 支持的格式和示例
            - 特殊要求或限制
        param2 (int, optional): 参数2的说明，默认值为1
    
    Returns:
        Dict[str, Any]: 返回结果的详细说明：
            - success (bool): 操作是否成功
            - data: 具体的数据结构说明
            - message (str): 状态消息
    
    使用建议：
    1. 具体的使用建议
    2. 性能优化提示
    3. 注意事项
    
    示例：
        result = await example_tool("示例参数", 2)
    """
    pass
```

#### 错误处理模式
```python
@mcp_server.tool()
async def robust_tool(query: str) -> Dict[str, Any]:
    """健壮的工具实现"""
    try:
        # 参数验证
        if not query or not query.strip():
            return {
                "success": False,
                "data": [],
                "message": "查询参数不能为空"
            }
        
        # 核心业务逻辑
        result = await some_crawl_function(query)
        
        # 结果验证
        if not result:
            return {
                "success": True,
                "data": [],
                "message": "未找到相关数据"
            }
        
        # 成功返回
        return {
            "success": True,
            "data": result,
            "total": len(result),
            "message": f"成功获取 {len(result)} 条数据"
        }
        
    except Exception as e:
        # 记录错误日志
        from fnewscrawler.utils.logger import LOGGER
        LOGGER.error(f"工具执行失败: {e}")
        
        # 返回错误信息
        return {
            "success": False,
            "data": [],
            "message": f"执行失败: {str(e)}"
        }
```

#### 返回数据标准化
```python
# 标准返回格式
{
    "success": bool,        # 操作是否成功
    "data": Any,           # 具体数据，类型根据工具而定
    "message": str,        # 状态消息
    "total": int,          # 数据总数（可选）
    "page": int,           # 当前页码（可选）
    "timestamp": str       # 时间戳（可选）
}

# 新闻数据格式
{
    "title": str,          # 新闻标题
    "content": str,        # 新闻内容或摘要
    "url": str,            # 新闻链接
    "time": str,           # 发布时间
    "source": str,         # 新闻来源
    "tags": List[str]      # 标签（可选）
}

# 市场数据格式
{
    "symbol": str,         # 股票代码
    "name": str,           # 股票名称
    "price": float,        # 当前价格
    "change": float,       # 涨跌额
    "change_percent": float, # 涨跌幅
    "volume": int,         # 成交量
    "timestamp": str       # 数据时间
}
```

### 3. 工具测试

#### 单元测试
```python
# test/mcp/test_new_site_tools.py
import pytest
from fnewscrawler.mcp.新站点名.crawl import new_site_news_query

@pytest.mark.asyncio
async def test_news_query_success():
    """测试新闻查询成功场景"""
    result = await new_site_news_query("测试查询", 1)
    
    assert isinstance(result, dict)
    assert "success" in result
    assert "data" in result
    assert "message" in result
    
    if result["success"]:
        assert isinstance(result["data"], list)
        if result["data"]:
            news_item = result["data"][0]
            assert "title" in news_item
            assert "url" in news_item

@pytest.mark.asyncio
async def test_news_query_empty_param():
    """测试空参数场景"""
    result = await new_site_news_query("", 1)
    
    assert result["success"] is False
    assert "参数不能为空" in result["message"]

@pytest.mark.asyncio
async def test_news_query_invalid_page():
    """测试无效页码场景"""
    result = await new_site_news_query("测试", 0)
    
    # 根据实际实现调整断言
    assert isinstance(result, dict)
```

#### 集成测试
```python
@pytest.mark.asyncio
async def test_mcp_server_integration():
    """测试MCP服务器集成"""
    from fnewscrawler.mcp import mcp_server
    
    # 获取所有工具
    tools = await mcp_server.get_tools()
    
    # 验证新工具已注册
    assert "new_site_news_query" in tools
    
    # 测试工具调用
    result = await mcp_server.call_tool(
        "new_site_news_query",
        query="测试",
        page_no=1
    )
    
    assert isinstance(result, dict)
```

### 4. 工具管理

#### 动态启用/禁用
```python
from fnewscrawler.mcp.mcp_manager import MCPManager

manager = MCPManager()

# 禁用工具
await manager.disable_tool("new_site_news_query")

# 启用工具
await manager.enable_tool("new_site_news_query")

# 检查工具状态
status = await manager.get_tool_status("new_site_news_query")
```

#### Web界面管理
访问 `http://localhost:8480/mcp` 进行可视化管理：
- 查看所有已注册的工具
- 动态启用/禁用工具
- 查看工具详细信息
- 批量操作工具状态

## 🔧 高级特性

### 1. 工具参数验证
```python
from pydantic import BaseModel, validator
from typing import Optional

class NewsQueryParams(BaseModel):
    query: str
    page_no: Optional[int] = 1
    
    @validator('query')
    def query_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('查询参数不能为空')
        return v.strip()
    
    @validator('page_no')
    def page_no_must_be_positive(cls, v):
        if v < 1:
            raise ValueError('页码必须大于0')
        return v

@mcp_server.tool()
async def validated_news_query(params: NewsQueryParams) -> Dict[str, Any]:
    """带参数验证的新闻查询工具"""
    # 参数已通过Pydantic验证
    return await some_crawl_function(params.query, params.page_no)
```

### 2. 工具缓存机制
```python
from functools import wraps
import json
import hashlib
from fnewscrawler.core.redis_manager import get_redis

def cache_result(expire_seconds: int = 300):
    """结果缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"mcp_cache:{func.__name__}:{hashlib.md5(json.dumps([args, kwargs], sort_keys=True).encode()).hexdigest()}"
            
            redis = get_redis()
            
            # 尝试从缓存获取
            cached_result = redis.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 缓存结果
            redis.setex(cache_key, expire_seconds, json.dumps(result))
            
            return result
        return wrapper
    return decorator

@mcp_server.tool()
@cache_result(expire_seconds=600)  # 缓存10分钟
async def cached_news_query(query: str) -> Dict[str, Any]:
    """带缓存的新闻查询"""
    return await some_crawl_function(query)
```

### 3. 工具监控和统计
```python
from functools import wraps
import time
from fnewscrawler.utils.logger import LOGGER

def monitor_tool(func):
    """工具监控装饰器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        tool_name = func.__name__
        
        try:
            result = await func(*args, **kwargs)
            
            # 记录成功调用
            duration = time.time() - start_time
            LOGGER.info(f"工具 {tool_name} 执行成功，耗时 {duration:.2f}秒")
            
            # 可以在此处记录统计信息到Redis
            
            return result
            
        except Exception as e:
            # 记录失败调用
            duration = time.time() - start_time
            LOGGER.error(f"工具 {tool_name} 执行失败，耗时 {duration:.2f}秒，错误: {e}")
            
            raise
    
    return wrapper

@mcp_server.tool()
@monitor_tool
async def monitored_tool(query: str) -> Dict[str, Any]:
    """带监控的工具"""
    return await some_function(query)
```

## 📊 性能优化

### 1. 异步并发
```python
import asyncio
from typing import List

@mcp_server.tool()
async def batch_news_query(queries: List[str]) -> Dict[str, Any]:
    """批量新闻查询"""
    try:
        # 并发执行多个查询
        tasks = [some_crawl_function(query) for query in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        success_results = []
        failed_queries = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_queries.append(queries[i])
            else:
                success_results.extend(result)
        
        return {
            "success": True,
            "data": success_results,
            "total": len(success_results),
            "failed_queries": failed_queries,
            "message": f"成功查询 {len(queries) - len(failed_queries)}/{len(queries)} 个关键词"
        }
        
    except Exception as e:
        return {
            "success": False,
            "data": [],
            "message": f"批量查询失败: {str(e)}"
        }
```



## 📋 开发检查清单

开发新MCP工具时，请确保完成以下检查：

### 基础开发
- [ ] 按域名创建MCP工具目录
- [ ] 实现工具函数并添加 `@mcp_server.tool()` 装饰器
- [ ] 编写详细的文档字符串
- [ ] 配置工具注册（__init__.py）
- [ ] 更新主MCP模块导入

### 代码质量
- [ ] 添加适当的错误处理
- [ ] 实现标准化的返回格式
- [ ] 添加参数验证
- [ ] 编写单元测试
- [ ] 编写集成测试

### 性能优化
- [ ] 考虑添加缓存机制
- [ ] 实现并发控制
- [ ] 添加监控和日志
- [ ] 性能测试和优化

### 文档和部署
- [ ] 更新工具使用文档
- [ ] 测试Web界面管理功能
- [ ] 验证工具启用/禁用功能
- [ ] 确认MCP客户端兼容性

## 🔍 调试技巧

### 1. 本地测试
```python
# 直接测试工具函数
from fnewscrawler.mcp.新站点名.crawl import new_site_news_query

result = await new_site_news_query("测试查询", 1)
print(result)
```

### 2. MCP服务器测试
```python
from fnewscrawler.mcp import mcp_server

# 测试工具注册
tools = await mcp_server.get_tools()
print("已注册的工具:", list(tools.keys()))

# 测试工具调用
result = await mcp_server.call_tool(
    "new_site_news_query",
    query="测试",
    page_no=1
)
print("调用结果:", result)
```

### 3. Web界面调试
1. 启动Web服务：`python main.py`
2. 访问 `http://localhost:8480/mcp`
3. 查看工具列表和状态
4. 测试工具启用/禁用功能

---

通过遵循本指南，您可以高效地开发出符合MCP协议标准的财经数据工具，为大模型提供专业的数据支持。如有疑问，请参考现有的 `iwencai` 工具实现或提交 Issue 寻求帮助。