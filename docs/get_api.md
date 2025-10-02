# GET API 接口文档

FNewsCrawler 提供了多种 GET 方法调用的接口，方便用户直接通过 HTTP 请求获取财经数据。本文档详细介绍了所有可用的 GET 接口。

## 📋 目录

1. [MCP 工具调用接口](#mcp-工具调用接口)
2. [AkShare 函数调用接口](#akshare-函数调用接口)
3. [通用数据提取工具接口](#通用数据提取工具接口)
4. [错误处理和最佳实践](#错误处理和最佳实践)

## 🔗 MCP 工具调用接口

### 基本调用方式

**端点**: `GET http://localhost:8480/api/mcp/call_tool/{tool_name}?xxxx`

**参数说明**:
- `tool_name`: MCP 工具名称
- `xxxx`: 工具所需的参数，通过 URL 查询参数传递

### 调用示例

```bash
# 调用行业股票资金流向工具
GET http://localhost:8480/api/mcp/call_tool/get_industry_stock_funds_flow_tool?industry_name=银行

# 调用新闻批量爬取工具（list 参数用逗号分隔）
GET http://localhost:8480/api/mcp/call_tool/news_crawl_batch?urls=http://example.com,http://example2.com
```

### 参数类型说明

- **字符串参数**: 直接传递值
- **列表参数**: 使用逗号分隔多个值
- **布尔参数**: 传递 `true` 或 `false`
- **数字参数**: 直接传递数字值

## 📊 AkShare 函数调用接口

### 基本调用方式

**端点**: `GET http://localhost:8480/api/mcp/call_akshare/{fun_name}?xxxx`

**参数说明**:
- `fun_name`: AkShare 函数名称
- `xxxx`: 函数参数，通过 URL 查询参数传递

### 支持的结果处理参数

| 参数名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `duplicate_key` | string | 去重字段 | `duplicate_key=变更日期` |
| `drop_columns` | string | 删除字段，多个字段用逗号分隔 | `drop_columns=流通受限股份,变动原因` |
| `return_type` | string | 返回类型，支持 `markdown` 或 `json`，默认 `markdown` | `return_type=json` |
| `filter_condition` | string | 筛选条件，类似 SQL 语法 | `filter_condition=交易所 == "SZ"` |
| `limit` | integer | 返回数据条数限制 | `limit=10` |
| `sort_by` | string | 排序字段 | `sort_by=日期` |
| `ascending` | boolean/integer/string | 排序方式，支持 `true/false`、`1/0`、`yes/no`，默认 `true` | `ascending=false` |

### 返回格式

```json
{
  "success": true,
  "message": "调用工具 {fun_name} 成功",
  "data": {
    "result": "函数执行结果（根据 return_type 决定格式）"
  }
}
```

### 调用示例

#### 基础调用
```bash
# 获取股票基本信息
GET http://localhost:8480/api/mcp/call_akshare/stock_zh_a_gbjg_em?symbol=603392.SH&return_type=json
```

#### 数据处理示例
```bash
# 去重和字段删除
GET http://localhost:8480/api/mcp/call_akshare/stock_zh_a_gbjg_em?duplicate_key=变更日期&drop_columns=流通受限股份,变动原因&return_type=json&symbol=603392.SH

# 条件筛选
GET http://localhost:8480/api/mcp/call_akshare/news_trade_notify_dividend_baidu?return_type=json&date=20240409&filter_condition=交易所 == "SZ"

# 排序和限制
GET http://localhost:8480/api/mcp/call_akshare/stock_zh_a_hist?symbol=000001&sort_by=日期&ascending=true&limit=10

# 复合条件
GET http://localhost:8480/api/mcp/call_akshare/stock_zh_a_hist?symbol=000001&filter_condition=收盘 > 10&sort_by=成交量&ascending=false&limit=3&drop_columns=变动因素
```

## 🔧 通用数据提取工具接口

### 结构化数据提取

**端点**: `GET http://localhost:8480/api/tools/extract-structured-data`

**参数说明**:

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| `url` | string | 是 | 要爬取的网页URL | `url=https://example.com` |
| `css_selector` | string | 是 | CSS选择器 | `css_selector=.news-title` |
| `context_name` | string | 否 | 浏览器context名称，默认 `default` | `context_name=my_context` |
| `extract_type` | string | 否 | 提取类型：`text`/`html`/`attribute`/`mixed`，默认 `text` | `extract_type=text` |
| `wait_for_selector` | string | 否 | 等待出现的特定选择器 | `wait_for_selector=.content` |
| `wait_timeout` | integer | 否 | 等待超时时间（毫秒），默认 `10000` | `wait_timeout=15000` |
| `multiple` | boolean | 否 | 是否提取多个元素，默认 `true` | `multiple=true` |
| `attributes` | string | 否 | 要提取的属性列表，逗号分隔 | `attributes=data-price,data-id` |
| `format_for_llm` | boolean | 否 | 是否格式化为便于LLM理解的文本，默认 `true` | `format_for_llm=true` |

**提取类型说明**:
- `text`: 提取文本内容
- `html`: 提取HTML内容
- `attribute`: 提取指定属性
- `mixed`: 混合提取（文本+HTML+属性）

**调用示例**:
```bash
# 提取新闻标题
GET http://localhost:8480/api/call_tools/extract-structured-data?url=https://example.com&css_selector=.news-title&extract_type=text&multiple=true

# 提取产品卡片信息（混合模式）
GET http://localhost:8480/api/call_tools/extract-structured-data?url=https://example.com&css_selector=.product-card&extract_type=mixed&attributes=data-price,data-id
```

### 表格数据提取

**端点**: `GET http://localhost:8480/api/call_tools/extract-table-data`

**参数说明**:

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| `url` | string | 是 | 包含表格的网页URL | `url=https://example.com` |
| `table_selector` | string | 否 | 表格的CSS选择器，默认 `table` | `table_selector=#data-table` |
| `context_name` | string | 否 | 浏览器context名称，默认 `default` | `context_name=my_context` |
| `include_header` | boolean | 否 | 是否包含表头，默认 `true` | `include_header=true` |
| `pandas_attrs` | string | 否 | pandas表格属性筛选（JSON格式） | `pandas_attrs={"id":"table1","class":"data-table"}` |
| `pandas_match` | string | 否 | pandas文本匹配模式 | `pandas_match=股票代码` |
| `pandas_header` | integer | 否 | pandas表头行号 | `pandas_header=0` |
| `pandas_skiprows` | string | 否 | pandas跳过的行数（单个数字或范围） | `pandas_skiprows=1` 或 `pandas_skiprows=1,2,3` 或 `pandas_skiprows=1:5` |
| `pandas_na_values` | string | 否 | pandas空值定义（逗号分隔） | `pandas_na_values=N/A,null,-` |
| `wait_timeout` | integer | 否 | 等待超时时间（毫秒），默认 `10000` | `wait_timeout=15000` |
| `format_for_llm` | boolean | 否 | 是否格式化为便于LLM理解的文本，默认 `true` | `format_for_llm=true` |
| `clean_data` | boolean | 否 | 是否进行数据清洗，默认 `true` | `clean_data=true` |
| `extract_links` | boolean | 否 | 是否提取表格中的链接，默认 `false` | `extract_links=false` |

**pandas选项详细说明**:
- `pandas_attrs`: JSON格式，用于根据HTML属性选择表格
- `pandas_match`: 根据表格中的文本内容匹配表格
- `pandas_header`: 指定哪一行作为表头
- `pandas_skiprows`: 支持多种格式
  - 单个数字：`"1"`
  - 逗号分隔：`"1,2,3"`
  - 范围格式：`"1:5"`
- `pandas_na_values`: 指定哪些值应该被转换为NaN

**调用示例**:
```bash
# 基础表格提取
GET http://localhost:8480/api/call_tools/extract-table-data?url=https://example.com&table_selector=#data-table

# 使用属性筛选表格
GET http://localhost:8480/api/call_tools/extract-table-data?url=https://example.com&pandas_attrs={"id":"stocks"}&clean_data=true

# 根据文本内容匹配表格
GET http://localhost:8480/api/call_tools/extract-table-data?url=https://example.com&pandas_match=股票代码&format_for_llm=true

# 复杂条件表格提取
GET http://localhost:8480/api/call_tools/extract-table-data?url=https://example.com&pandas_header=1&pandas_skiprows=2,3&pandas_na_values=N/A,-&clean_data=true
```

## ⚠️ 错误处理和最佳实践

### 常见错误类型

1. **参数格式错误**
```bash
# ❌ 错误：参数值加了引号
GET http://localhost:8480/api/mcp/call_akshare/stock_zh_a_gbjg_em?symbol="603392.SH"&return_type=json

# ✅ 正确：直接传递参数值
GET http://localhost:8480/api/mcp/call_akshare/stock_zh_a_gbjg_em?symbol=603392.SH&return_type=json
```

2. **JSON 格式错误**
```bash
# ❌ 错误：JSON 格式不正确
GET http://localhost:8480/api/call_tools/extract-table-data?pandas_attrs={id:table1}

# ✅ 正确：使用标准 JSON 格式
GET http://localhost:8480/api/call_tools/extract-table-data?pandas_attrs={"id":"table1"}
```

3. **字段名错误**
```bash
# ❌ 错误：sort_by 字段必须是返回数据中的实际列名
GET http://localhost:8480/api/mcp/call_akshare/stock_zh_a_hist?sort_by=不存在的字段

# ✅ 正确：使用实际的列名
GET http://localhost:8480/api/mcp/call_akshare/stock_zh_a_hist?sort_by=日期
```

### 最佳实践建议

1. **参数传递**
   - 不要给参数值添加引号（单引号或双引号）
   - `filter_condition` 参数除外，该参数内部可以使用引号
   - 列表参数使用逗号分隔
   - 布尔参数使用 `true`/`false`

2. **数据处理**
   - 使用 `limit` 参数控制返回数据量，避免响应过大
   - 使用 `filter_condition` 进行数据筛选，减少不必要的数据传输
   - 使用 `drop_columns` 删除不需要的字段
   - 使用 `sort_by` 和 `limit` 配合获取最新的 N 条数据

3. **错误处理**
   - 检查响应中的 `success` 字段
   - 查看返回的 `message` 了解错误详情
   - 使用 `return_type=json` 获取结构化数据便于程序处理

4. **性能优化**
   - 合理设置 `wait_timeout` 避免过长等待
   - 使用 `context_name` 进行会话管理
   - 大量数据提取时考虑分页处理

## 🔗 相关文档

- [项目主文档](../README.md)
- [Docker 部署指南](../docker/README.md)
- [MCP 协议说明](https://modelcontextprotocol.io/)
- [AkShare 官方文档](https://www.akshare.xyz/)

## 📞 技术支持

如有问题或建议，请提交 [Issue](https://github.com/noimank/FNewsCrawler/issues) 或查看 [项目文档](../README.md)。