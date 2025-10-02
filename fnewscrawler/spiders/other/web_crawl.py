from io import StringIO
from typing import Dict, Any, List, Optional, Union

import pandas as pd

from fnewscrawler.core.context import context_manager
from fnewscrawler.utils.logger import LOGGER


async def extract_structured_data(
    url: str,
    css_selector: str,
    context_name: str = "default",
    extract_type: str = "text",
    wait_for_selector: Optional[str] = None,
    wait_timeout: int = 10000,
    multiple: bool = True,
    attributes: Optional[List[str]] = None,
    format_for_llm: bool = True
) -> Dict[str, Any]:
    """
    从指定URL和CSS选择器中提取结构化信息，专为AI大语言模型优化

    Args:
        url (str): 要爬取的网页URL
        css_selector (str): CSS选择器，用于定位要提取的元素
        context_name (str): 浏览器context名称，用于会话管理，默认为"default"
        extract_type (str): 提取类型，可选 "text", "html", "attribute", "mixed"，默认为"text"
        wait_for_selector (str, optional): 等待出现的特定选择器，确保动态内容加载完成
        wait_timeout (int): 等待超时时间（毫秒），默认10000
        multiple (bool): 是否提取多个元素，True为提取所有匹配的元素，False为只提取第一个
        attributes (List[str], optional): 当extract_type为"attribute"时，指定要提取的属性列表
        format_for_llm (bool): 是否将数据格式化为便于大语言模型理解的文本格式，默认为True

    Returns:
        Dict[str, Any]: 包含提取结果的字典
            - success (bool): 是否成功提取数据
            - data (Union[str, List[Dict]]): 提取的数据，根据format_for_llm参数返回不同格式
            - raw_data (List[Dict]): 原始结构化数据（当format_for_llm=True时提供）
            - count (int): 提取的元素数量
            - url (str): 源URL
            - selector (str): 使用的CSS选择器
            - extract_type (str): 使用的提取类型
            - message (str): 状态消息
            - formatted_summary (str): 为AI模型准备的格式化摘要（当format_for_llm=True时提供）

    Raises:
        Exception: 当网页访问失败或数据提取出错时抛出
    """
    try:
        LOGGER.info(f"开始从 {url} 提取数据，选择器: {css_selector}, context: {context_name}")

        # 获取或创建浏览器上下文
        context = await context_manager.get_context(context_name)
        page = await context.new_page()

        # 设置用户代理
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

        result_data = {
            "success": False,
            "data": [] if multiple else "",
            "raw_data": [],
            "count": 0,
            "url": url,
            "selector": css_selector,
            "extract_type": extract_type,
            "message": "",
            "formatted_summary": ""
        }

        try:
            # 访问目标网页
            LOGGER.info(f"正在访问网页: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # 如果指定了等待的选择器，等待其出现
            if wait_for_selector:
                LOGGER.info(f"等待选择器出现: {wait_for_selector}")
                try:
                    await page.wait_for_selector(wait_for_selector, timeout=wait_timeout)
                except Exception as e:
                    LOGGER.warning(f"等待选择器超时: {wait_for_selector}, 错误: {e}")
                    # 继续执行，不抛出异常

            # 定位目标元素
            elements = page.locator(css_selector)
            element_count = await elements.count()

            if element_count == 0:
                result_data["message"] = f"未找到匹配选择器 '{css_selector}' 的元素"
                LOGGER.warning(result_data["message"])
                return result_data

            LOGGER.info(f"找到 {element_count} 个匹配的元素")

            # 提取数据
            extracted_data = []

            if multiple:
                # 提取所有匹配的元素
                for i in range(element_count):
                    element = elements.nth(i)
                    element_data = await _extract_element_data(
                        element, extract_type, attributes, i
                    )
                    if element_data:
                        extracted_data.append(element_data)
            else:
                # 只提取第一个元素
                element = elements.first
                element_data = await _extract_element_data(
                    element, extract_type, attributes, 0
                )
                extracted_data = element_data if isinstance(element_data, dict) else [element_data]

            # 设置返回结果
            result_data["success"] = True
            result_data["raw_data"] = extracted_data if isinstance(extracted_data, list) else [extracted_data]
            result_data["count"] = element_count
            result_data["message"] = f"成功提取 {element_count} 个元素的数据"

            # 根据format_for_llm参数格式化数据
            if format_for_llm:
                result_data["formatted_summary"] = _format_data_for_llm(extracted_data, extract_type, url, css_selector)
                result_data["data"] = result_data["formatted_summary"] if multiple else (result_data["formatted_summary"] if extracted_data else "")
            else:
                result_data["data"] = extracted_data if multiple else (extracted_data[0] if extracted_data else "")

            LOGGER.info(result_data["message"])

        finally:
            # 关闭页面
            await page.close()

        return result_data

    except Exception as e:
        error_msg = f"提取数据失败: {str(e)}"
        LOGGER.error(error_msg)

        return {
            "success": False,
            "data": "" if format_for_llm else ([] if multiple else ""),
            "raw_data": [],
            "count": 0,
            "url": url,
            "selector": css_selector,
            "extract_type": extract_type,
            "message": error_msg,
            "formatted_summary": ""
        }


async def _extract_element_data(
    element,
    extract_type: str,
    attributes: Optional[List[str]],
    index: int
) -> Union[Dict[str, Any], str, None]:
    """
    提取单个元素的数据

    Args:
        element: Playwright元素对象
        extract_type (str): 提取类型
        attributes (List[str], optional): 要提取的属性列表
        index (int): 元素索引

    Returns:
        Union[Dict[str, Any], str, None]: 提取的数据
    """
    try:
        if extract_type == "text":
            return await element.text_content()

        elif extract_type == "html":
            return await element.inner_html()

        elif extract_type == "attribute":
            if not attributes:
                # 如果没有指定属性，提取所有属性
                attrs = await element.get_attribute_keys()
                element_data = {"index": index}
                for attr in attrs:
                    value = await element.get_attribute(attr)
                    element_data[attr] = value
                return element_data
            else:
                # 提取指定属性
                element_data = {"index": index}
                for attr in attributes:
                    value = await element.get_attribute(attr)
                    element_data[attr] = value
                return element_data

        elif extract_type == "mixed":
            # 混合提取：文本、HTML和属性
            element_data = {
                "index": index,
                "text": await element.text_content(),
                "html": await element.inner_html()
            }

            # 提取常用属性
            common_attrs = ["href", "src", "alt", "title", "class", "id"]
            for attr in common_attrs:
                value = await element.get_attribute(attr)
                if value is not None:
                    element_data[attr] = value

            # 如果指定了额外属性，也提取
            if attributes:
                for attr in attributes:
                    if attr not in common_attrs:
                        value = await element.get_attribute(attr)
                        if value is not None:
                            element_data[attr] = value

            return element_data

        else:
            LOGGER.warning(f"不支持的提取类型: {extract_type}")
            return None

    except Exception as e:
        LOGGER.error(f"提取元素数据失败 (索引: {index}): {str(e)}")
        return None


def _format_data_for_llm(
    data: Union[List[Dict], Dict, str],
    extract_type: str,
    url: str,
    css_selector: str
) -> str:
    """
    将提取的数据格式化为便于大语言模型理解的文本格式

    Args:
        data: 提取的原始数据
        extract_type (str): 提取类型
        url (str): 源URL
        css_selector (str): CSS选择器

    Returns:
        str: 格式化后的文本
    """
    if not data:
        return "未找到匹配的数据"

    # 构建标题信息
    summary_parts = [
        f"网页数据提取结果",
        f"来源URL: {url}",
        f"选择器: {css_selector}",
        f"提取类型: {extract_type}",
        "-" * 50
    ]

    if isinstance(data, str):
        # 简单文本内容
        summary_parts.append(f"提取内容:\n{data}")

    elif isinstance(data, list):
        # 列表数据
        if len(data) == 1:
            # 单个元素
            item = data[0]
            if isinstance(item, str):
                summary_parts.append(f"提取内容:\n{item}")
            elif isinstance(item, dict):
                summary_parts.append(f"提取内容:\n{_format_dict_for_llm(item)}")
        else:
            # 多个元素
            summary_parts.append(f"共找到 {len(data)} 个匹配元素:")

            for i, item in enumerate(data, 1):
                summary_parts.append(f"\n【元素 {i}】")
                if isinstance(item, str):
                    summary_parts.append(item)
                elif isinstance(item, dict):
                    summary_parts.append(_format_dict_for_llm(item))

    elif isinstance(data, dict):
        # 字典数据
        summary_parts.append(f"提取内容:\n{_format_dict_for_llm(data)}")

    return "\n".join(summary_parts)


def _format_dict_for_llm(data: Dict[str, Any]) -> str:
    """
    将字典数据格式化为便于LLM阅读的文本

    Args:
        data: 字典数据

    Returns:
        str: 格式化后的文本
    """
    if not data:
        return "空数据"

    formatted_lines = []

    # 特殊处理包含text字段的情况
    if "text" in data:
        text_content = data["text"]
        if text_content and text_content.strip():
            formatted_lines.append(f"文本内容: {text_content.strip()}")

        # 处理其他字段
        other_fields = {k: v for k, v in data.items() if k != "text"}
        if other_fields:
            formatted_lines.append("其他属性:")
            for key, value in other_fields.items():
                if key != "index":  # 跳过索引字段
                    formatted_lines.append(f"  {key}: {value}")
    else:
        # 常规字典处理
        for key, value in data.items():
            if key != "index":  # 跳过索引字段
                if isinstance(value, str) and len(value) > 200:
                    # 长文本截断
                    value = value[:200] + "..."
                formatted_lines.append(f"{key}: {value}")

    return "\n".join(formatted_lines)


async def extract_table_data(
    url: str,
    table_selector: str = "table",
    context_name: str = "default",
    include_header: bool = True,
    pandas_options: Optional[Dict[str, Any]] = None,
    wait_timeout: int = 10000,
    format_for_llm: bool = True,
    clean_data: bool = True,
    extract_links: bool = False
) -> Dict[str, Any]:
    """
    使用pandas实现的成熟表格数据提取函数，支持高级数据清洗和格式化

    Args:
        url (str): 包含表格的网页URL
        table_selector (str): 表格的CSS选择器，默认为"table"
        context_name (str): 浏览器context名称
        include_header (bool): 是否包含表头，默认为True
        pandas_options (Dict[str, Any], optional): pandas.read_html的参数选项
            - attrs: 根据HTML属性筛选表格 {"id": "table1", "class": "data-table"}
            - match: 根据文本内容匹配表格
            - header: 指定表头行号
            - index_col: 指定索引列
            - skiprows: 跳过的行数
            - na_values: 转换为NaN的值
            - keep_default_na: 是否保留默认NaN值
            - converters: 列数据转换器
        wait_timeout (int): 等待超时时间（毫秒）
        format_for_llm (bool): 是否将数据格式化为便于大语言模型理解的文本格式
        clean_data (bool): 是否进行数据清洗，默认为True
        extract_links (bool): 是否提取表格中的链接，默认为False

    Returns:
        Dict[str, Any]: 包含表格数据的字典
            - success (bool): 是否成功
            - data (Union[str, List[Dict]]): 表格数据
            - raw_data (List[Dict]): 原始表格数据
            - pandas_dataframe (Dict): pandas DataFrame信息（列名、数据类型等）
            - headers (List[str]): 表头列表
            - row_count (int): 行数
            - column_count (int): 列数
            - data_quality (Dict): 数据质量指标
            - formatted_summary (str): 格式化摘要
    """
    try:
        LOGGER.info(f"开始从 {url} 提取表格数据（pandas增强版）")

        # 默认pandas选项
        default_options = {
            "attrs": None,
            "match": None,
            "header": 0 if include_header else None,
            "index_col": None,
            "skiprows": None,
            "na_values": ["", "N/A", "n/a", "NULL", "null", "-"],
            "keep_default_na": True,
            "converters": None,
            "extract_links": "all" if extract_links else None
        }

        # 合并用户提供的选项
        if pandas_options:
            default_options.update(pandas_options)

        # 获取浏览器上下文
        context = await context_manager.get_context(context_name)
        page = await context.new_page()

        result_data = {
            "success": False,
            "data": [],
            "raw_data": [],
            "pandas_dataframe": {},
            "headers": [],
            "row_count": 0,
            "column_count": 0,
            "url": url,
            "table_selector": table_selector,
            "message": "",
            "formatted_summary": "",
            "data_quality": {}
        }

        try:
            # 访问网页
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # 等待表格加载
            await page.wait_for_selector(table_selector, timeout=wait_timeout)

            # 提取表格HTML内容
            table_html = await page.locator(table_selector).first.inner_html()

            # 构建完整的表格HTML
            full_table_html = f"<table>{table_html}</table>"

            LOGGER.info("开始使用pandas解析表格HTML")

            # 使用pandas的read_html方法解析表格
            try:
                # 创建pandas解析选项
                pd_options = {}
                for key, value in default_options.items():
                    if value is not None:
                        pd_options[key] = value

                # 使用pandas读取HTML表格
                dfs = pd.read_html(StringIO(full_table_html), **pd_options)

                if not dfs:
                    result_data["message"] = "pandas未能解析出任何表格数据"
                    LOGGER.warning(result_data["message"])
                    return result_data

                # 取第一个表格（主要表格）
                df = dfs[0]

                LOGGER.info(f"pandas成功解析表格：{df.shape[0]} 行 x {df.shape[1]} 列")

            except Exception as pandas_error:
                LOGGER.warning(f"pandas解析失败，回退到基础方法: {str(pandas_error)}")
                # 回退到基础提取方法
                return await _fallback_table_extraction(
                    page, table_selector, result_data, include_header, format_for_llm, url
                )

            # 数据清洗
            if clean_data:
                df = _clean_dataframe(df)

            # 提取基本统计信息
            data_quality = _analyze_data_quality(df)

            # 转换为字典格式
            table_data = df.to_dict('records')
            headers = df.columns.tolist()

            # 提取DataFrame元信息
            dataframe_info = {
                "columns": headers,
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "shape": df.shape,
                "memory_usage": df.memory_usage(deep=True).sum(),
                "null_counts": df.isnull().sum().to_dict()
            }

            # 设置结果
            result_data["success"] = True
            result_data["raw_data"] = table_data
            result_data["pandas_dataframe"] = dataframe_info
            result_data["headers"] = headers
            result_data["row_count"] = len(table_data)
            result_data["column_count"] = len(headers)
            result_data["data_quality"] = data_quality
            result_data["message"] = f"成功提取表格数据：{len(table_data)} 行 x {len(headers)} 列（pandas增强版）"

            # 格式化数据
            if format_for_llm:
                result_data["formatted_summary"] = _format_enhanced_table_for_llm(
                    table_data, headers, dataframe_info, data_quality, url
                )
                result_data["data"] = result_data["formatted_summary"]
            else:
                result_data["data"] = table_data

            LOGGER.info(result_data["message"])

        finally:
            await page.close()

        return result_data

    except Exception as e:
        error_msg = f"提取表格数据失败: {str(e)}"
        LOGGER.error(error_msg)

        return {
            "success": False,
            "data": "" if format_for_llm else [],
            "raw_data": [],
            "pandas_dataframe": {},
            "headers": [],
            "row_count": 0,
            "column_count": 0,
            "url": url,
            "table_selector": table_selector,
            "message": error_msg,
            "formatted_summary": "",
            "data_quality": {}
        }


def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    使用pandas进行数据清洗

    Args:
        df: 原始DataFrame

    Returns:
        pd.DataFrame: 清洗后的DataFrame
    """
    try:
        # 创建副本避免修改原数据
        cleaned_df = df.copy()

        # 1. 清理列名：去除多余空白字符
        cleaned_df.columns = cleaned_df.columns.str.strip()

        # 2. 转换数据类型：尝试将看起来像数字的列转换为数值类型
        for col in cleaned_df.columns:
            if cleaned_df[col].dtype == 'object':
                # 尝试转换为数值类型
                cleaned_df[col] = pd.to_numeric(cleaned_df[col])

        # 3. 清理字符串数据：去除前后空白
        string_columns = cleaned_df.select_dtypes(include=['object']).columns
        for col in string_columns:
            cleaned_df[col] = cleaned_df[col].astype(str).str.strip()

        # 4. 处理空值：用列的众数填充数值列，用"未知"填充字符串列
        for col in cleaned_df.columns:
            if cleaned_df[col].isnull().any():
                if cleaned_df[col].dtype in ['int64', 'float64']:
                    # 数值列用中位数填充
                    median_val = cleaned_df[col].median()
                    cleaned_df[col].fillna(median_val, inplace=True)
                else:
                    # 字符串列用"未知"填充
                    cleaned_df[col].fillna("未知", inplace=True)

        # 5. 移除完全空的行和列
        cleaned_df.dropna(how='all', inplace=True)
        cleaned_df.dropna(axis=1, how='all', inplace=True)

        LOGGER.info(f"数据清洗完成：{df.shape} -> {cleaned_df.shape}")
        return cleaned_df

    except Exception as e:
        LOGGER.warning(f"数据清洗失败，返回原始数据: {str(e)}")
        return df


def _analyze_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """
    分析数据质量

    Args:
        df: DataFrame

    Returns:
        Dict[str, Any]: 数据质量指标
    """
    quality_metrics = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "null_count": df.isnull().sum().sum(),
        "duplicate_rows": df.duplicated().sum(),
        "data_types": df.dtypes.value_counts().to_dict(),
        "column_stats": {}
    }

    # 分析每列的统计信息
    for col in df.columns:
        col_stats = {
            "data_type": str(df[col].dtype),
            "null_count": df[col].isnull().sum(),
            "unique_count": df[col].nunique(),
            "empty_string_count": (df[col] == '').sum() if df[col].dtype == 'object' else 0
        }

        # 数值列的额外统计
        if df[col].dtype in ['int64', 'float64']:
            col_stats.update({
                "mean": float(df[col].mean()) if not df[col].empty else None,
                "std": float(df[col].std()) if not df[col].empty else None,
                "min": float(df[col].min()) if not df[col].empty else None,
                "max": float(df[col].max()) if not df[col].empty else None
            })

        # 字符串列的额外统计
        elif df[col].dtype == 'object':
            avg_length = df[col].astype(str).str.len().mean()
            col_stats["avg_string_length"] = float(avg_length) if not pd.isna(avg_length) else 0

        quality_metrics["column_stats"][col] = col_stats

    return quality_metrics


async def _fallback_table_extraction(
    page,
    table_selector: str,
    result_data: Dict[str, Any],
    include_header: bool,
    format_for_llm: bool,
    url: str
) -> Dict[str, Any]:
    """
    当pandas解析失败时的回退提取方法

    Args:
        page: Playwright页面对象
        table_selector: 表格选择器
        result_data: 结果数据字典
        include_header: 是否包含表头
        format_for_llm: 是否格式化为LLM格式
        url: 源URL

    Returns:
        Dict[str, Any]: 提取结果
    """
    try:
        LOGGER.info("使用回退方法提取表格数据")

        # 定位表格
        table_element = page.locator(table_selector).first

        # 提取表头
        headers = []
        if include_header:
            header_rows = table_element.locator("thead tr, tr:first-child")
            if await header_rows.count() > 0:
                header_cells = header_rows.first.locator("th, td")
                header_count = await header_cells.count()

                for i in range(header_count):
                    header_text = await header_cells.nth(i).text_content()
                    headers.append(header_text.strip() if header_text else f"Column_{i+1}")

        # 提取数据行
        rows = table_element.locator("tr")
        row_count = await rows.count()

        table_data = []

        for row_idx in range(row_count):
            # 跳过表头行（如果已经提取了表头）
            if include_header and row_idx == 0 and await rows.nth(row_idx).locator("th").count() > 0:
                continue

            row_data = {}
            cells = rows.nth(row_idx).locator("td,th")
            cell_count = await cells.count()

            for cell_idx in range(cell_count):
                cell_text = await cells.nth(cell_idx).text_content()
                column_name = headers[cell_idx] if cell_idx < len(headers) else f"Column_{cell_idx+1}"
                row_data[column_name] = cell_text.strip() if cell_text else ""

            if row_data:  # 只添加非空行
                table_data.append(row_data)

        # 设置结果
        result_data["success"] = True
        result_data["raw_data"] = table_data
        result_data["headers"] = headers
        result_data["row_count"] = len(table_data)
        result_data["column_count"] = len(headers) if headers else 0
        result_data["message"] = f"成功提取表格数据（回退方法）：{len(table_data)} 行 x {len(headers) if headers else 0} 列"

        # 格式化数据
        if format_for_llm:
            result_data["formatted_summary"] = _format_table_for_llm(table_data, headers, url)
            result_data["data"] = result_data["formatted_summary"]
        else:
            result_data["data"] = table_data

        return result_data

    except Exception as e:
        result_data["message"] = f"回退方法也失败: {str(e)}"
        return result_data


def _format_enhanced_table_for_llm(
    table_data: List[Dict[str, Any]],
    headers: List[str],
    dataframe_info: Dict[str, Any],
    data_quality: Dict[str, Any],
    url: str
) -> str:
    """
    将增强版表格数据格式化为便于大语言模型理解的文本格式

    Args:
        table_data: 表格数据
        headers: 表头
        dataframe_info: DataFrame元信息
        data_quality: 数据质量指标
        url: 源URL

    Returns:
        str: 格式化后的表格文本
    """
    if not table_data:
        return "表格数据为空"

    summary_parts = [
        "📊 表格数据提取结果（Pandas增强版）",
        f"📍 来源URL: {url}",
        f"📏 表格规模: {data_quality['total_rows']} 行 x {data_quality['total_columns']} 列",
        f"💾 内存使用: {dataframe_info['memory_usage']:,} 字节",
        f"🔍 数据质量: {data_quality['null_count']} 个空值, {data_quality['duplicate_rows']} 个重复行",
        "=" * 60
    ]

    # 添加列信息
    summary_parts.append("📋 列信息:")
    for col in headers:
        dtype = dataframe_info['dtypes'][col]
        null_count = data_quality['column_stats'][col]['null_count']
        unique_count = data_quality['column_stats'][col]['unique_count']
        summary_parts.append(f"  • {col} ({dtype}) - {unique_count} 个唯一值, {null_count} 个空值")

    # 添加表头
    summary_parts.append("\n📑 表头:")
    header_line = " | ".join([f"{h:15}" for h in headers])
    summary_parts.append(header_line)
    summary_parts.append("=" * len(header_line))

    # 添加数据样本（前10行）
    summary_parts.append("📄 数据样本（前10行）:")
    sample_data = table_data[:10]
    for i, row in enumerate(sample_data, 1):
        row_values = []
        for header in headers:
            value = str(row.get(header, ""))[:30] + ("..." if len(str(row.get(header, ""))) > 30 else "")
            row_values.append(f"{value:15}")

        row_line = f"行{i}: " + " | ".join(row_values)
        summary_parts.append(row_line)

    # 添加数值列统计
    numeric_cols = [col for col, dtype in dataframe_info['dtypes'].items() if 'int' in dtype or 'float' in dtype]
    if numeric_cols:
        summary_parts.append("\n📈 数值列统计:")
        for col in numeric_cols[:5]:  # 只显示前5个数值列
            stats = data_quality['column_stats'][col]
            if stats.get('mean') is not None:
                summary_parts.append(f"  • {col}: 平均值={stats['mean']:.2f}, 范围=[{stats['min']:.2f}, {stats['max']:.2f}]")

    # 添加总结
    summary_parts.extend([
        "=" * 60,
        f"✅ 数据提取完成: 共 {data_quality['total_rows']} 行 x {data_quality['total_columns']} 列有效数据",
        f"🎯 建议注意: {'存在缺失值' if data_quality['null_count'] > 0 else '数据完整'}, "
        f"{'存在重复行' if data_quality['duplicate_rows'] > 0 else '无重复'}"
    ])

    return "\n".join(summary_parts)


def _format_table_for_llm(
    table_data: List[Dict[str, str]],
    headers: List[str],
    url: str
) -> str:
    """
    将表格数据格式化为便于大语言模型理解的文本格式（基础版本）

    Args:
        table_data: 表格数据
        headers: 表头
        url: 源URL

    Returns:
        str: 格式化后的表格文本
    """
    if not table_data:
        return "表格数据为空"

    summary_parts = [
        f"表格数据提取结果",
        f"来源URL: {url}",
        f"表格规模: {len(table_data)} 行 x {len(headers)} 列",
        "-" * 50
    ]

    # 添加表头信息
    if headers:
        summary_parts.append("表头:")
        header_line = " | ".join(headers)
        summary_parts.append(header_line)
        summary_parts.append("-" * len(header_line))

    # 添加数据行
    summary_parts.append("数据内容:")
    for i, row in enumerate(table_data, 1):
        row_values = []
        for header in headers:
            value = row.get(header, "")
            if value:
                # 限制单元格内容长度，避免过长
                if len(value) > 100:
                    value = value[:100] + "..."
                row_values.append(value)
            else:
                row_values.append("")

        if any(row_values):  # 只显示非空行
            row_line = f"行{i}: {' | '.join(row_values)}"
            summary_parts.append(row_line)

    # 添加统计信息
    summary_parts.append("-" * 50)
    summary_parts.append(f"总计: {len(table_data)} 行有效数据")

    return "\n".join(summary_parts)