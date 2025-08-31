import json

import akshare as ak

from fnewscrawler.utils import parse_params2list, format_param


def ak_super_fun(fun_name: str, duplicate_key="", drop_columns: str = "", return_type: str = 'json',
                 **kwargs) -> dict | str:
    """调用akshare的函数
    
    Args:
        fun_name: akshare函数名称
        duplicate_key: 去重键，可以指定根据哪一列进行去重
        drop_columns: 要删除的列名，多个列名用逗号分隔
        return_type: 返回类型，可选'json'或'markdown'，默认'json'
        **kwargs: 函数参数
    
    Returns:
        Any: 函数返回结果
        
    Raises:
        AttributeError: 当函数不存在时抛出
        Exception: 函数执行出错时抛出
    """
    try:
        # 获取ak模块中的函数对象
        fun = getattr(ak, fun_name)
        duplicate_key = format_param(duplicate_key, str)
        drop_columns = format_param(drop_columns, str)
        return_type = format_param(return_type, str)

        # 执行函数并返回结果
        df = fun(**kwargs)
        if duplicate_key in df.columns:
            df = df.drop_duplicates(subset=[duplicate_key])
        else:
            df = df.drop_duplicates()
        df = df.reset_index(drop=True)
        if drop_columns:
            drop_columns = parse_params2list(drop_columns, str)
            df = df.drop(columns=drop_columns)

        if return_type == 'markdown':
            df = df.to_markdown(index=False)
        elif return_type == "json":
            df = df.to_json(orient='records', force_ascii=False)
            df = json.loads(df)
        else:
            raise ValueError(f"不支持的返回类型: {return_type}, 仅支持json或者markdown")
        return df

    except AttributeError as e:
        # 处理函数不存在的情况
        raise AttributeError(f"akshare中不存在函数: {fun_name}") from e

    except Exception as e:
        # 处理函数执行错误的情况
        raise Exception(f"执行函数{fun_name}时出错: {str(e)}") from e
