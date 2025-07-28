from fnewscrawler.mcp import mcp_server

@mcp_server.tool()
def iwencai_news_query(query):
    return f"search {query}"


