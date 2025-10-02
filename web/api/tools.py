import json
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from fnewscrawler.spiders.other.web_crawl import extract_structured_data, extract_table_data
from fnewscrawler.utils.logger import LOGGER

# 创建路由器
router = APIRouter()


class APIResponse(BaseModel):
    success: bool
    message: str
    data: dict | str | list = None


@router.get("/extract-structured-data", response_model=APIResponse)
async def api_extract_structured_data(
    request: Request,
    url: str = Query(..., description="要爬取的网页URL"),
    css_selector: str = Query(..., description="CSS选择器，用于定位要提取的元素"),
    context_name: str = Query("default", description="浏览器context名称，用于会话管理"),
    extract_type: str = Query("text", description="提取类型：text/html/attribute/mixed"),
    wait_for_selector: Optional[str] = Query(None, description="等待出现的特定选择器"),
    wait_timeout: int = Query(10000, description="等待超时时间（毫秒）"),
    multiple: bool = Query(True, description="是否提取多个元素"),
    attributes: Optional[str] = Query(None, description="要提取的属性列表，逗号分隔"),
    format_for_llm: bool = Query(True, description="是否格式化为便于大语言模型理解的文本")
):
    """
    从指定URL和CSS选择器中提取结构化信息

    支持多种提取类型：
    - text: 提取文本内容
    - html: 提取HTML内容
    - attribute: 提取指定属性
    - mixed: 混合提取（文本+HTML+属性）

    使用示例：
    GET /api/tools/extract-structured-data?url=https://example.com&css_selector=.news-title&extract_type=text&multiple=true
    GET /api/tools/extract-structured-data?url=https://example.com&css_selector=.product-card&extract_type=mixed&attributes=data-price,data-id
    """
    try:
        # 处理属性列表
        attr_list = None
        if attributes:
            attr_list = [attr.strip() for attr in attributes.split(',') if attr.strip()]

        # 调用提取函数
        result = await extract_structured_data(
            url=url,
            css_selector=css_selector,
            context_name=context_name,
            extract_type=extract_type,
            wait_for_selector=wait_for_selector,
            wait_timeout=wait_timeout,
            multiple=multiple,
            attributes=attr_list,
            format_for_llm=format_for_llm
        )

        if result["success"]:
            return APIResponse(
                success=True,
                message=f"成功提取 {result['count']} 个元素的数据",
                data={
                    "extracted_data": result["data"],
                    "raw_data": result["raw_data"],
                    "count": result["count"],
                    "url": result["url"],
                    "selector": result["selector"],
                    "extract_type": result["extract_type"],
                    "formatted_summary": result.get("formatted_summary", "")
                }
            )
        else:
            return APIResponse(
                success=False,
                message=result["message"],
                data={}
            )

    except Exception as e:
        LOGGER.error(f"提取结构化数据API调用失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"提取数据失败: {str(e)}")


@router.get("/extract-table-data", response_model=APIResponse)
async def api_extract_table_data(
    request: Request,
    url: str = Query(..., description="包含表格的网页URL"),
    table_selector: str = Query("table", description="表格的CSS选择器"),
    context_name: str = Query("default", description="浏览器context名称"),
    include_header: bool = Query(True, description="是否包含表头"),
    pandas_attrs: Optional[str] = Query(None, description="pandas表格属性筛选（JSON格式）"),
    pandas_match: Optional[str] = Query(None, description="pandas文本匹配模式"),
    pandas_header: Optional[int] = Query(None, description="pandas表头行号"),
    pandas_skiprows: Optional[str] = Query(None, description="pandas跳过的行数（单个数字或范围）"),
    pandas_na_values: Optional[str] = Query(None, description="pandas空值定义（逗号分隔）"),
    wait_timeout: int = Query(10000, description="等待超时时间（毫秒）"),
    format_for_llm: bool = Query(True, description="是否格式化为便于大语言模型理解的文本"),
    clean_data: bool = Query(True, description="是否进行数据清洗"),
    extract_links: bool = Query(False, description="是否提取表格中的链接")
):
    """
    使用pandas实现的成熟表格数据提取函数，支持高级数据清洗和格式化

    pandas选项说明：
    - pandas_attrs: JSON格式，如 {"id": "table1", "class": "data-table"}
    - pandas_match: 根据文本内容匹配表格
    - pandas_header: 指定表头行号
    - pandas_skiprows: 跳过的行数，如 "1" 或 "1,2,3" 或 "1:5"
    - pandas_na_values: 转换为NaN的值，如 "N/A,null,-"

    使用示例：
    GET /api/tools/extract-table-data?url=https://example.com&table_selector=#data-table
    GET /api/tools/extract-table-data?url=https://example.com&pandas_attrs={"id":"stocks"}&clean_data=true
    GET /api/tools/extract-table-data?url=https://example.com&pandas_match=股票代码&format_for_llm=true
    """
    try:
        # 构建pandas选项
        pandas_options = {}

        # 处理属性筛选
        if pandas_attrs:
            try:
                pandas_options["attrs"] = json.loads(pandas_attrs)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="pandas_attrs必须是有效的JSON格式")

        # 处理其他pandas选项
        if pandas_match:
            pandas_options["match"] = pandas_match

        if pandas_header is not None:
            pandas_options["header"] = pandas_header

        if pandas_skiprows:
            try:
                # 处理跳过行数的不同格式
                if ":" in pandas_skiprows:
                    # 范围格式，如 "1:5"
                    start, end = map(int, pandas_skiprows.split(":"))
                    pandas_options["skiprows"] = range(start, end)
                elif "," in pandas_skiprows:
                    # 逗号分隔，如 "1,2,3"
                    pandas_options["skiprows"] = [int(x.strip()) for x in pandas_skiprows.split(",")]
                else:
                    # 单个数字
                    pandas_options["skiprows"] = int(pandas_skiprows)
            except ValueError:
                raise HTTPException(status_code=400, detail="pandas_skiprows格式不正确")

        if pandas_na_values:
            pandas_options["na_values"] = [v.strip() for v in pandas_na_values.split(",") if v.strip()]

        # 调用表格提取函数
        result = await extract_table_data(
            url=url,
            table_selector=table_selector,
            context_name=context_name,
            include_header=include_header,
            pandas_options=pandas_options if pandas_options else None,
            wait_timeout=wait_timeout,
            format_for_llm=format_for_llm,
            clean_data=clean_data,
            extract_links=extract_links
        )

        if result["success"]:
            return APIResponse(
                success=True,
                message=result["message"],
                data={
                    "extracted_data": result["data"],
                    "raw_data": result["raw_data"],
                    "pandas_dataframe": result["pandas_dataframe"],
                    "headers": result["headers"],
                    "row_count": result["row_count"],
                    "column_count": result["column_count"],
                    "data_quality": result["data_quality"],
                    "url": result["url"],
                    "table_selector": result["table_selector"],
                    "formatted_summary": result.get("formatted_summary", "")
                }
            )
        else:
            return APIResponse(
                success=False,
                message=result["message"],
                data={}
            )

    except HTTPException:
        raise
    except Exception as e:
        LOGGER.error(f"提取表格数据API调用失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"提取表格数据失败: {str(e)}")

