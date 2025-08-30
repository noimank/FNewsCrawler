
import akshare as ak


def stock_cyq_em(stock_code: str, adjust:str="")->str:
    """
       东方财富网-概念板-行情中心-日K-筹码分布
       https://quote.eastmoney.com/concept/sz000001.html
       :param stock_code: 股票代码,如 000001
       :type stock_code: str
       :param adjust: choice of {"qfq": "前复权", "hfq": "后复权", "": "不复权"}
       :type adjust: str
       :return: 筹码分布
       :rtype: str
   """

    stock_cyq_em_df = ak.stock_cyq_em(symbol=stock_code, adjust=adjust)
    if  stock_cyq_em_df.empty:
        return f"akshare: {stock_code}的筹码数据为空"
    md = stock_cyq_em_df.to_markdown(index=False)
    return md




