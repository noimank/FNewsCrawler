
def parse_params2list(params: str , data_type=int) -> list:
    """解析参数字符串为列表，主要的应用场景是为了解决用户采用get方法调用mcp函数时处理list类型的参数
    Args:
        params (str): 参数字符串，格式为'1,2,3'或'[1,2,3]'
        data_type (type, optional): 解析后的数据类型，默认为int

    Returns:
        list: 解析后的参数列表
    """
    if isinstance(params, list):
        return [data_type(p) for p in params]

    if isinstance(params, data_type):
        return [params]

    # 转换为英文符号
    if isinstance(params, str) and "，" in params:
        params = params.replace("，", ",")

    if params.startswith('[') and params.endswith(']'):
        params = params[1:-1]

    elif params.startswith('(') and params.endswith(')'):
        params = params[1:-1]
    elif params.startswith('{') and params.endswith('}'):
        params = params[1:-1]
    elif params.startswith('"') and params.endswith('"'):
        params = params[1:-1]
    elif params.startswith("'") and params.endswith("'"):
        params = params[1:-1]

    return [data_type(p.strip()) for p in params.split(',')]



def  format_param(param, param_type :type):
    """
    格式化参数，都是为了将参数转换为指定的类型
    Args:
        param (any): 参数
        param_type (type): 参数类型
    Returns:
        any: 格式化后的参数
    """
    if isinstance(param, param_type):
        return param
    if isinstance(param, str):
        param = param.strip()
        return param_type(param)

    raise ValueError(f"参数{param}不能转换为{param_type}类型")




