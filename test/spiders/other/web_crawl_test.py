import asyncio
from unittest.mock import Mock, AsyncMock, patch

from fnewscrawler.spiders.other.web_crawl import (
    extract_structured_data,
    extract_table_data,
    _extract_element_data,
    _format_data_for_llm,
    _format_dict_for_llm,
    _clean_dataframe,
    _analyze_data_quality
)


async def test_extract_structured_data_text():
    """测试文本提取功能"""
    # 使用一个简单的测试网站
    url = "https://stockpage.10jqka.com.cn/002121/"
    css_selector = ".new_trading fl"

    # Mock browser context and page
    with patch('fnewscrawler.spiders.other.web_crawl.context_manager.get_context') as mock_context:
        mock_ctx = AsyncMock()
        mock_page = AsyncMock()
        mock_ctx.new_page.return_value = mock_page
        mock_context.return_value = mock_ctx

        # Mock page elements
        mock_element = AsyncMock()
        mock_element.text_content.return_value = "Example Domain"

        mock_locator = Mock()
        mock_locator.count.return_value = 1
        mock_locator.first.return_value = mock_element

        mock_page.locator.return_value = mock_locator
        mock_page.goto.return_value = None

        # 测试提取文本
        result = await extract_structured_data(
            url=url,
            css_selector=css_selector,
            extract_type="text",
            multiple=False
        )


        assert result["success"] is True
        assert "Example Domain" in result["data"]
        assert result["count"] == 1
        assert result["url"] == url
        assert result["selector"] == css_selector


async def test_extract_structured_data_multiple():
    """测试提取多个元素"""
    url = "https://example.com"
    css_selector = "p"

    with patch('fnewscrawler.spiders.other.web_crawl.context_manager.get_context') as mock_context:
        mock_ctx = AsyncMock()
        mock_page = AsyncMock()
        mock_ctx.new_page.return_value = mock_page
        mock_context.return_value = mock_ctx

        # Mock multiple elements
        mock_element1 = AsyncMock()
        mock_element1.text_content.return_value = "Paragraph 1"

        mock_element2 = AsyncMock()
        mock_element2.text_content.return_value = "Paragraph 2"

        mock_locator = Mock()
        mock_locator.count.return_value = 2
        mock_locator.nth.side_effect = [mock_element1, mock_element2]

        mock_page.locator.return_value = mock_locator
        mock_page.goto.return_value = None

        result = await extract_structured_data(
            url=url,
            css_selector=css_selector,
            extract_type="text",
            multiple=True
        )

        assert result["success"] is True
        assert "Paragraph 1" in result["data"]
        assert "Paragraph 2" in result["data"]
        assert result["count"] == 2


async def test_extract_structured_data_no_elements():
    """测试没有找到元素的情况"""
    url = "https://example.com"
    css_selector = ".non-existent"

    with patch('fnewscrawler.spiders.other.web_crawl.context_manager.get_context') as mock_context:
        mock_ctx = AsyncMock()
        mock_page = AsyncMock()
        mock_ctx.new_page.return_value = mock_page
        mock_context.return_value = mock_ctx

        # Mock no elements found
        mock_locator = Mock()
        mock_locator.count.return_value = 0

        mock_page.locator.return_value = mock_locator
        mock_page.goto.return_value = None

        result = await extract_structured_data(
            url=url,
            css_selector=css_selector
        )

        assert result["success"] is False
        assert result["count"] == 0
        assert "未找到匹配选择器" in result["message"]


async def test_extract_element_data_text():
    """测试单个元素文本提取"""
    mock_element = AsyncMock()
    mock_element.text_content.return_value = "Test text content"

    result = await _extract_element_data(
        element=mock_element,
        extract_type="text",
        attributes=None,
        index=0
    )

    assert result == "Test text content"


async def test_extract_element_data_html():
    """测试单个元素HTML提取"""
    mock_element = AsyncMock()
    mock_element.inner_html.return_value = "<div>HTML content</div>"

    result = await _extract_element_data(
        element=mock_element,
        extract_type="html",
        attributes=None,
        index=0
    )

    assert result == "<div>HTML content</div>"


async def test_extract_element_data_attribute():
    """测试单个元素属性提取"""
    mock_element = AsyncMock()
    mock_element.get_attribute_keys.return_value = ["href", "class", "id"]
    mock_element.get_attribute.side_effect = lambda attr: {
        "href": "https://example.com",
        "class": "test-class",
        "id": "test-id"
    }.get(attr)

    result = await _extract_element_data(
        element=mock_element,
        extract_type="attribute",
        attributes=None,
        index=0
    )

    assert result["index"] == 0
    assert result["href"] == "https://example.com"
    assert result["class"] == "test-class"
    assert result["id"] == "test-id"


async def test_extract_element_data_mixed():
    """测试混合提取（文本、HTML、属性）"""
    mock_element = AsyncMock()
    mock_element.text_content.return_value = "Text content"
    mock_element.inner_html.return_value = "<div>HTML content</div>"
    mock_element.get_attribute.side_effect = lambda attr: {
        "href": "https://example.com",
        "class": "test-class"
    }.get(attr)

    result = await _extract_element_data(
        element=mock_element,
        extract_type="mixed",
        attributes=["custom-attr"],
        index=1
    )

    assert result["index"] == 1
    assert result["text"] == "Text content"
    assert result["html"] == "<div>HTML content</div>"
    assert result["href"] == "https://example.com"
    assert result["class"] == "test-class"


def test_format_data_for_llm_text():
    """测试文本数据的LLM格式化"""
    data = "Simple text content"
    url = "https://example.com"
    css_selector = "h1"
    extract_type = "text"

    result = _format_data_for_llm(data, extract_type, url, css_selector)

    assert "网页数据提取结果" in result
    assert url in result
    assert css_selector in result
    assert extract_type in result
    assert "Simple text content" in result


def test_format_data_for_llm_list():
    """测试列表数据的LLM格式化"""
    data = ["Item 1", "Item 2", "Item 3"]
    url = "https://example.com"
    css_selector = "li"
    extract_type = "text"

    result = _format_data_for_llm(data, extract_type, url, css_selector)

    assert "共找到 3 个匹配元素" in result
    assert "Item 1" in result
    assert "Item 2" in result
    assert "Item 3" in result


def test_format_data_for_llm_dict():
    """测试字典数据的LLM格式化"""
    data = {"text": "Content text", "href": "https://example.com", "class": "test"}
    url = "https://example.com"
    css_selector = "a"
    extract_type = "mixed"

    result = _format_data_for_llm(data, extract_type, url, css_selector)

    assert "文本内容: Content text" in result
    assert "href: https://example.com" in result
    assert "class: test" in result


def test_format_dict_for_llm_with_text():
    """测试包含text字段的字典格式化"""
    data = {
        "text": "Main content",
        "href": "https://example.com",
        "class": "link-class",
        "index": 0
    }

    result = _format_dict_for_llm(data)

    assert "文本内容: Main content" in result
    assert "其他属性:" in result
    assert "href: https://example.com" in result
    assert "class: link-class" in result
    assert "index" not in result  # 应该跳过index字段


def test_format_dict_for_llm_regular():
    """测试常规字典格式化"""
    data = {
        "name": "Test Product",
        "price": 99.99,
        "description": "This is a test product with a very long description that should be truncated"
    }

    result = _format_dict_for_llm(data)

    assert "name: Test Product" in result
    assert "price: 99.99" in result
    assert "description: This is a test product with a very long description that should be trunc..." in result


async def test_extract_table_data_basic():
    """测试基础表格数据提取"""
    url = "https://example.com/table"
    table_selector = "table"

    with patch('fnewscrawler.spiders.other.web_crawl.context_manager.get_context') as mock_context:
        mock_ctx = AsyncMock()
        mock_page = AsyncMock()
        mock_ctx.new_page.return_value = mock_page
        mock_context.return_value = mock_ctx

        # Mock table HTML
        table_html = """
        <thead>
            <tr><th>Name</th><th>Age</th><th>City</th></tr>
        </thead>
        <tbody>
            <tr><td>John</td><td>25</td><td>New York</td></tr>
            <tr><td>Jane</td><td>30</td><td>London</td></tr>
        </tbody>
        """

        mock_locator = Mock()
        mock_locator.first.inner_html.return_value = table_html

        mock_page.locator.return_value = mock_locator
        mock_page.goto.return_value = None
        mock_page.wait_for_selector.return_value = None

        # Mock pandas read_html
        with patch('pandas.read_html') as mock_read_html:
            import pandas as pd
            test_df = pd.DataFrame([
                {"Name": "John", "Age": 25, "City": "New York"},
                {"Name": "Jane", "Age": 30, "City": "London"}
            ])
            mock_read_html.return_value = [test_df]

            result = await extract_table_data(
                url=url,
                table_selector=table_selector
            )

            assert result["success"] is True
            assert result["row_count"] == 2
            assert result["column_count"] == 3
            assert "Name" in result["headers"]
            assert "Age" in result["headers"]
            assert "City" in result["headers"]


def test_clean_dataframe():
    """测试DataFrame清洗功能"""
    import pandas as pd
    import numpy as np

    # 创建测试数据
    df = pd.DataFrame({
        "name": ["  Alice  ", "  Bob  ", "  Charlie  "],
        "age": ["25", "30", "35"],
        "score": [85.5, 90.0, np.nan],
        "description": ["Good", "", None]
    })

    cleaned_df = _clean_dataframe(df)

    # 检查字符串去除空白
    assert cleaned_df["name"].iloc[0] == "Alice"
    assert cleaned_df["name"].iloc[1] == "Bob"

    # 检查数值转换
    assert pd.api.types.is_numeric_dtype(cleaned_df["age"])

    # 检查空值处理
    assert cleaned_df["score"].iloc[2] == 87.75  # 中位数填充
    assert cleaned_df["description"].iloc[3] == "未知"  # 未知字符串填充


def test_analyze_data_quality():
    """测试数据质量分析"""
    import pandas as pd
    import numpy as np

    df = pd.DataFrame({
        "numeric_col": [1, 2, 3, 4, 5],
        "text_col": ["A", "B", "A", "C", None],
        "float_col": [1.1, 2.2, 3.3, 4.4, 5.5]
    })

    quality = _analyze_data_quality(df)

    assert quality["total_rows"] == 5
    assert quality["total_columns"] == 3
    assert quality["null_count"] == 1
    assert quality["duplicate_rows"] == 0

    # 检查列统计
    col_stats = quality["column_stats"]["numeric_col"]
    assert col_stats["data_type"] == "int64"
    assert col_stats["null_count"] == 0
    assert col_stats["unique_count"] == 5
    assert col_stats["mean"] == 3.0
    assert col_stats["min"] == 1.0
    assert col_stats["max"] == 5.0


# if __name__ == "__main__":
#     # 运行所有测试
#     async def run_all_tests():
#         print("开始测试 web_crawl 模块...")
#
#         try:
#             await test_extract_structured_data_text()
#             print("✓ test_extract_structured_data_text 通过")
#         except Exception as e:
#             print(f"✗ test_extract_structured_data_text 失败: {e}")
#
#         try:
#             await test_extract_structured_data_multiple()
#             print("✓ test_extract_structured_data_multiple 通过")
#         except Exception as e:
#             print(f"✗ test_extract_structured_data_multiple 失败: {e}")
#
#         try:
#             await test_extract_structured_data_no_elements()
#             print("✓ test_extract_structured_data_no_elements 通过")
#         except Exception as e:
#             print(f"✗ test_extract_structured_data_no_elements 失败: {e}")
#
#         try:
#             await test_extract_element_data_text()
#             print("✓ test_extract_element_data_text 通过")
#         except Exception as e:
#             print(f"✗ test_extract_element_data_text 失败: {e}")
#
#         try:
#             await test_extract_element_data_html()
#             print("✓ test_extract_element_data_html 通过")
#         except Exception as e:
#             print(f"✗ test_extract_element_data_html 失败: {e}")
#
#         try:
#             await test_extract_element_data_attribute()
#             print("✓ test_extract_element_data_attribute 通过")
#         except Exception as e:
#             print(f"✗ test_extract_element_data_attribute 失败: {e}")
#
#         try:
#             await test_extract_element_data_mixed()
#             print("✓ test_extract_element_data_mixed 通过")
#         except Exception as e:
#             print(f"✗ test_extract_element_data_mixed 失败: {e}")
#
#         try:
#             test_format_data_for_llm_text()
#             print("✓ test_format_data_for_llm_text 通过")
#         except Exception as e:
#             print(f"✗ test_format_data_for_llm_text 失败: {e}")
#
#         try:
#             test_format_data_for_llm_list()
#             print("✓ test_format_data_for_llm_list 通过")
#         except Exception as e:
#             print(f"✗ test_format_data_for_llm_list 失败: {e}")
#
#         try:
#             test_format_data_for_llm_dict()
#             print("✓ test_format_data_for_llm_dict 通过")
#         except Exception as e:
#             print(f"✗ test_format_data_for_llm_dict 失败: {e}")
#
#         try:
#             test_format_dict_for_llm_with_text()
#             print("✓ test_format_dict_for_llm_with_text 通过")
#         except Exception as e:
#             print(f"✗ test_format_dict_for_llm_with_text 失败: {e}")
#
#         try:
#             test_format_dict_for_llm_regular()
#             print("✓ test_format_dict_for_llm_regular 通过")
#         except Exception as e:
#             print(f"✗ test_format_dict_for_llm_regular 失败: {e}")
#
#         try:
#             await test_extract_table_data_basic()
#             print("✓ test_extract_table_data_basic 通过")
#         except Exception as e:
#             print(f"✗ test_extract_table_data_basic 失败: {e}")
#
#         try:
#             test_clean_dataframe()
#             print("✓ test_clean_dataframe 通过")
#         except Exception as e:
#             print(f"✗ test_clean_dataframe 失败: {e}")
#
#         try:
#             test_analyze_data_quality()
#             print("✓ test_analyze_data_quality 通过")
#         except Exception as e:
#             print(f"✗ test_analyze_data_quality 失败: {e}")
#
#         print("测试完成!")
#
#     loop = asyncio.new_event_loop()
#     loop.run_until_complete(run_all_tests())
#     loop.close()



async def  test_cn():
    url = "https://finance.eastmoney.com/a/202510013527998954.html"
    css_selector = ".txtinfos"
    result = await extract_structured_data(
        url=url,
        css_selector=css_selector,
        extract_type="text",
        wait_for_selector=css_selector,
        multiple=False
    )
    print(result)

async def  test_table():
    url = "https://stockpage.10jqka.com.cn/002121/"
    css_selector = ".table_sscjfb.mt4"
    result = await extract_table_data(
        url=url,
        table_selector=css_selector,
        context_name="iwencai"
    )
    print(result)



if __name__ == '__main__':
    asyncio.run(test_cn())
    # asyncio.run(test_table())


