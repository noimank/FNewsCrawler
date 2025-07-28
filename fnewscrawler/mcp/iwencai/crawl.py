from fnewscrawler.mcp import mcp_server

@mcp_server.tool()
def iwencai_news_query(query):
    """
    iwencai_news_query 工具函数
    用于查询iwencai新闻
    :param query: 查询字符串
    :return: 查询结果
    """
    return f"search {query}"


@mcp_server.tool()
def iwencai_test(query):
    """
    iwencai_news_query 工具函数
    ### Adding Components

    Your converted MCP server is a full FastMCP instance, meaning you can add new tools, resources, and other components to it just like you would with any other FastMCP instance.

    ```python {8-11}
    # Assumes the FastAPI app from above is already defined
    from fastmcp import FastMCP

    # Convert to MCP server
    mcp = FastMCP.from_fastapi(app=app)

    # Add a new tool
    @mcp.tool
    def get_product(product_id: int) -> ProductResponse:

        return products_db[product_id]

    # Run the MCP server
    if __name__ == "__main__":
        mcp.run()
    ```
    用于查询iwencai新闻

    :param query: 查询字符串
    :return: 查询结果
    """
    return f"search {query}"


