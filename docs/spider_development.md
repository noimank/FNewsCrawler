# 爬虫开发指南

## 📖 概述

FNewsCrawler 采用模块化的爬虫架构设计，基于 Playwright 浏览器自动化技术，为财经数据采集提供高效、稳定的解决方案。本文档详细介绍了爬虫系统的设计理念、架构组件和开发规范。

## 🏗️ 架构设计

### 核心设计理念

1. **域名组织原则**：所有爬虫按目标网站域名进行组织，确保代码结构清晰
2. **单例模式管理**：采用单例模式管理浏览器实例，提高资源利用效率
3. **上下文共享机制**：同域名下的所有操作共享浏览器上下文，维护会话状态
4. **统一登录框架**：提供标准化的二维码登录基类，简化登录实现
5. **异步优先设计**：全面采用异步编程模式，支持高并发访问

### 系统架构图

```
爬虫系统架构
├── 🌐 BrowserManager (单例)
│   ├── Playwright 实例管理
│   ├── 浏览器生命周期控制
│   ├── 健康检查与自动恢复
│   └── 资源清理与优化
│
├── 🔄 ContextManager (单例)
│   ├── 域名级上下文隔离
│   ├── 会话状态持久化
│   ├── 自动清理过期上下文
│   └── 并发访问控制
│
├── 🔐 QRLoginBase (抽象基类)
│   ├── 二维码获取接口
│   ├── 登录状态验证
│   ├── 会话状态保存
│   └── 登录状态管理
│
└── 🕷️ Spider Modules (按域名组织)
    ├── iwencai/
    │   ├── login.py    # 登录实现
    │   ├── crawl.py    # 爬虫逻辑
    │   └── __init__.py # 模块导出
    ├── eastmoney/
    └── 其他站点.../
```

## 🧩 核心组件详解

### 1. BrowserManager - 浏览器管理器

**位置**: `fnewscrawler/core/browser.py`

**设计特点**:
- 单例模式确保全局唯一浏览器实例
- 支持 headless/headed 模式切换
- 自动健康检查和故障恢复
- 优雅的资源清理机制

**核心方法**:
```python
class BrowserManager:
    async def initialize(self) -> None:
        """初始化浏览器实例"""
    
    async def get_browser(self) -> Browser:
        """获取浏览器实例，自动处理重连"""
    
    async def get_browser_info(self) -> dict:
        """获取浏览器状态信息"""
    
    async def force_restart(self) -> None:
        """强制重启浏览器"""
```

**使用示例**:
```python
from fnewscrawler.core.browser import browser_manager

# 获取浏览器实例
browser = await browser_manager.get_browser()
```

### 2. ContextManager - 上下文管理器

**位置**: `fnewscrawler/core/context.py`

**设计特点**:
- 按域名隔离浏览器上下文
- 自动维护登录状态和Cookie
- 支持上下文的创建、获取、刷新和清理
- Redis持久化存储会话状态

**核心方法**:
```python
class ContextManager:
    async def get_context(self, site_name: str, force_new: bool = False) -> BrowserContext:
        """获取指定站点的浏览器上下文"""
    
    async def save_context_state(self, site_name: str) -> bool:
        """保存上下文状态到Redis"""
    
    async def refresh_context(self, site_name: str) -> BrowserContext:
        """刷新指定站点的上下文"""
    
    async def get_context_stats(self) -> Dict[str, Any]:
        """获取上下文统计信息"""
```

**使用示例**:
```python
from fnewscrawler.core.context import context_manager

# 获取iwencai站点的上下文
context = await context_manager.get_context("iwencai")
page = await context.new_page()
```

### 3. QRLoginBase - 二维码登录基类

**位置**: `fnewscrawler/core/qr_login_base.py`

**设计特点**:
- 抽象基类定义标准登录接口
- 单例模式减少实例化开销
- 统一的登录流程和状态管理
- 支持多种二维码登录方式

**抽象方法**:
```python
class QRLoginBase(ABC):
    @abstractmethod
    async def get_qr_code(self, qr_type: str = "微信") -> Tuple[bool, str]:
        """获取登录二维码"""
    
    @abstractmethod
    async def verify_login_success(self) -> bool:
        """验证登录是否成功"""
    
    @abstractmethod
    async def save_context_state(self):
        """保存浏览器状态到Redis"""
    
    @abstractmethod
    async def get_login_status(self) -> bool:
        """获取当前登录状态"""
    
    @abstractmethod
    async def clean_login_state(self) -> bool:
        """清理登录状态"""
    
    @abstractmethod
    def get_supported_qr_types(self) -> List[str]:
        """获取支持的二维码类型"""
```

## 📁 目录结构规范

### 爬虫模块组织

```
fnewscrawler/spiders/
├── __init__.py
├── iwencai/                    # 同花顺问财
│   ├── __init__.py            # 模块导出
│   ├── login.py               # 登录实现
│   ├── crawl.py               # 爬虫逻辑
│   └── utils.py               # 工具函数（可选）
├── eastmoney/                  # 东方财富
│   ├── __init__.py
│   ├── login.py
│   ├── crawl.py
│   └── utils.py
└── 新站点/                     # 新增站点
    ├── __init__.py
    ├── login.py               # 如需登录
    ├── crawl.py
    └── utils.py
```

### 文件命名规范

- **login.py**: 登录相关逻辑，继承 `QRLoginBase`
- **crawl.py**: 核心爬虫逻辑，数据提取和处理
- **utils.py**: 站点特定的工具函数（可选）
- **__init__.py**: 模块导出，暴露主要接口

## 🛠️ 开发实践

### 1. 创建新爬虫模块

**步骤1: 创建目录结构**
```bash
mkdir fnewscrawler/spiders/新站点名
touch fnewscrawler/spiders/新站点名/__init__.py
touch fnewscrawler/spiders/新站点名/crawl.py
touch fnewscrawler/spiders/新站点名/login.py  # 如需登录
```

**步骤2: 实现登录类（如需要）**
```python
# fnewscrawler/spiders/新站点名/login.py
from typing import Tuple, List
from fnewscrawler.core.qr_login_base import QRLoginBase
from fnewscrawler.utils.logger import LOGGER

class NewSiteLogin(QRLoginBase):
    def __init__(self):
        super().__init__()
        self.base_url = "https://新站点域名.com"
        self.login_page = None
    
    async def get_qr_code(self, qr_type: str = "微信") -> Tuple[bool, str]:
        """获取登录二维码"""
        try:
            # 获取站点上下文
            context = await self.context_manager.get_context("新站点名")
            self.login_page = await context.new_page()
            
            # 导航到登录页面
            await self.login_page.goto(self.base_url)
            
            # 点击登录按钮
            await self.login_page.click("登录按钮选择器")
            
            # 选择二维码登录方式
            if qr_type == "微信":
                await self.login_page.click("微信登录选择器")
            
            # 等待二维码加载
            await self.login_page.wait_for_selector("二维码选择器")
            
            # 获取二维码URL
            qr_element = self.login_page.locator("二维码选择器")
            qr_url = await qr_element.get_attribute("src")
            
            return True, qr_url
            
        except Exception as e:
            LOGGER.error(f"获取二维码失败: {e}")
            return False, str(e)
    
    async def verify_login_success(self) -> bool:
        """验证登录是否成功"""
        try:
            # 等待登录成功的标志元素
            await self.login_page.wait_for_selector(
                "登录成功标志选择器", 
                timeout=30000
            )
            return True
        except Exception as e:
            LOGGER.warning(f"登录验证失败: {e}")
            return False
    
    async def save_context_state(self):
        """保存浏览器状态"""
        await self.context_manager.save_context_state("新站点名")
    
    async def get_login_status(self) -> bool:
        """获取登录状态"""
        try:
            context = await self.context_manager.get_context("新站点名")
            page = await context.new_page()
            await page.goto(self.base_url)
            
            # 检查是否存在登录状态标志
            is_logged_in = await page.locator("登录状态标志选择器").count() > 0
            await page.close()
            
            return is_logged_in
        except Exception as e:
            LOGGER.error(f"检查登录状态失败: {e}")
            return False
    
    async def clean_login_state(self) -> bool:
        """清理登录状态"""
        try:
            await self.context_manager.delete_context_state("新站点名")
            return True
        except Exception as e:
            LOGGER.error(f"清理登录状态失败: {e}")
            return False
    
    def get_supported_qr_types(self) -> List[str]:
        """获取支持的二维码类型"""
        return ["微信", "QQ"]  # 根据实际支持的类型调整
```

**步骤3: 实现爬虫逻辑**
```python
# fnewscrawler/spiders/新站点名/crawl.py
from typing import List, Dict, Optional
from fnewscrawler.core.context import context_manager
from fnewscrawler.utils.logger import LOGGER

async def new_site_crawl_from_query(query: str, page_no: int = 1) -> List[Dict[str, str]]:
    """从新站点获取数据"""
    try:
        # 获取站点上下文
        context = await context_manager.get_context("新站点名")
        page = await context.new_page()
        
        # 构建搜索URL
        search_url = f"https://新站点域名.com/search?q={query}&page={page_no}"
        
        # 导航到搜索页面
        await page.goto(search_url)
        await page.wait_for_load_state("domcontentloaded")
        
        # 提取数据
        results = []
        items = page.locator("数据项选择器")
        count = await items.count()
        
        for i in range(count):
            item = items.nth(i)
            
            # 提取标题
            title_element = item.locator("标题选择器")
            title = await title_element.text_content() if await title_element.count() > 0 else ""
            
            # 提取链接
            link_element = item.locator("链接选择器")
            link = await link_element.get_attribute("href") if await link_element.count() > 0 else ""
            
            # 提取时间
            time_element = item.locator("时间选择器")
            time = await time_element.text_content() if await time_element.count() > 0 else ""
            
            # 提取来源
            source_element = item.locator("来源选择器")
            source = await source_element.text_content() if await source_element.count() > 0 else ""
            
            results.append({
                "title": title.strip(),
                "url": link,
                "time": time.strip(),
                "source": source.strip(),
                "content": ""  # 如需要可进一步提取内容
            })
        
        await page.close()
        return results
        
    except Exception as e:
        LOGGER.error(f"爬取新站点数据失败: {e}")
        return []
```

**步骤4: 配置模块导出**
```python
# fnewscrawler/spiders/新站点名/__init__.py
from .crawl import new_site_crawl_from_query
from .login import NewSiteLogin  # 如有登录功能

__all__ = ["new_site_crawl_from_query", "NewSiteLogin"]
```

### 2. 最佳实践

#### 错误处理
```python
try:
    # 爬虫逻辑
    pass
except Exception as e:
    LOGGER.error(f"操作失败: {e}")
    # 适当的错误恢复逻辑
    return []  # 或其他默认值
```

#### 等待策略
```python
# 等待页面加载
await page.wait_for_load_state("domcontentloaded")

# 等待特定元素
await page.wait_for_selector("选择器", timeout=10000)

# 等待网络空闲
await page.wait_for_load_state("networkidle")
```

#### 数据提取
```python
# 安全的文本提取
title = await element.text_content() if await element.count() > 0 else ""

# 安全的属性提取
link = await element.get_attribute("href") if await element.count() > 0 else ""

# 批量元素处理
items = page.locator("选择器")
count = await items.count()
for i in range(count):
    item = items.nth(i)
    # 处理单个元素
```

#### 资源管理
```python
# 及时关闭页面
try:
    page = await context.new_page()
    # 页面操作
finally:
    await page.close()

# 或使用上下文管理器
async with context.new_page() as page:
    # 页面操作
    pass  # 自动关闭
```

## 🔍 调试技巧

### 1. 启用可视化模式
```bash
# 设置环境变量
export PW_USE_HEADLESS=false

# 或在代码中设置
os.environ["PW_USE_HEADLESS"] = "false"
```

### 2. 添加调试日志
```python
from fnewscrawler.utils.logger import LOGGER

LOGGER.debug(f"当前页面URL: {page.url}")
LOGGER.info(f"找到 {count} 个数据项")
```

### 3. 截图调试
```python
# 保存页面截图
await page.screenshot(path="debug.png")

# 保存特定元素截图
await element.screenshot(path="element.png")
```

### 4. 页面内容检查
```python
# 打印页面HTML
html = await page.content()
print(html)

# 检查元素是否存在
if await page.locator("选择器").count() > 0:
    print("元素存在")
```

## 📊 性能优化

### 1. 上下文复用
```python
# 好的做法：复用上下文
context = await context_manager.get_context("站点名")
for query in queries:
    page = await context.new_page()
    # 处理查询
    await page.close()

# 避免：频繁创建新上下文
for query in queries:
    context = await context_manager.get_context("站点名", force_new=True)  # 不推荐
```

### 2. 并发控制
```python
import asyncio
from asyncio import Semaphore

# 限制并发数
semaphore = Semaphore(5)  # 最多5个并发

async def crawl_with_limit(query):
    async with semaphore:
        return await crawl_function(query)

# 批量处理
tasks = [crawl_with_limit(query) for query in queries]
results = await asyncio.gather(*tasks)
```

### 3. 资源清理
```python
# 定期清理过期上下文
await context_manager._cleanup_expired_contexts()

# 手动清理特定上下文
await context_manager.close_site_context("站点名")
```

## 🧪 测试指南

### 1. 单元测试
```python
import pytest
from fnewscrawler.spiders.新站点名 import new_site_crawl_from_query

@pytest.mark.asyncio
async def test_crawl_function():
    results = await new_site_crawl_from_query("测试查询")
    assert isinstance(results, list)
    if results:
        assert "title" in results[0]
        assert "url" in results[0]
```

### 2. 集成测试
```python
@pytest.mark.asyncio
async def test_login_flow():
    login = NewSiteLogin()
    
    # 测试二维码获取
    success, qr_url = await login.get_qr_code()
    assert success
    assert qr_url.startswith("http")
    
    # 测试登录状态检查
    status = await login.get_login_status()
    assert isinstance(status, bool)
```

## 📋 检查清单

开发新爬虫时，请确保完成以下检查：

- [ ] 按域名创建目录结构
- [ ] 实现必要的登录类（如需要）
- [ ] 实现核心爬虫逻辑
- [ ] 配置模块导出
- [ ] 添加适当的错误处理
- [ ] 编写单元测试
- [ ] 测试登录流程（如有）
- [ ] 测试数据提取功能
- [ ] 验证资源清理
- [ ] 性能测试和优化

---

通过遵循本指南，您可以高效地开发出稳定、可维护的财经数据爬虫模块。如有疑问，请参考现有的 `iwencai` 模块实现或提交 Issue 寻求帮助。