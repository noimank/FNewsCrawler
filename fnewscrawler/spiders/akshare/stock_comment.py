import akshare as ak


def ak_stock_comment_detail(stock_code: str) -> str:
    """从akshare获取股票机构参与度,大约最近的44个交易日的数据

    Args:
        stock_code: 股票代码，如'600000'

    Returns:
        包含股票机构参与度数据的markdown表格，列名包括：日期、机构参与度
    """
    stock_comment_detail_zlkp_jgcyd_em_df = ak.stock_comment_detail_zlkp_jgcyd_em(symbol=stock_code)
    # 重命名列
    stock_comment_detail_zlkp_jgcyd_em_df = stock_comment_detail_zlkp_jgcyd_em_df.rename(columns={ "机构参与度": "机构参与度（%）"})
    markdown_table = stock_comment_detail_zlkp_jgcyd_em_df.to_markdown(index=False)

    return markdown_table
