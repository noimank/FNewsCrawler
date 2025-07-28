from urllib.parse import urlparse

def extract_second_level_domain(url: str) -> str | None:
    """
    从给定的网址中提取二级域名名称。

    Args:
        url (str): 完整的网址字符串，例如 "https://www.example.com", "blog.sub.domain.co.uk"

    Returns:
        str | None: 提取到的二级域名名称（不包含顶级域名），
                    如果无法提取则返回 None。
    Example:
        >>> extract_second_level_domain("https://www.example.com")
        'example'
        >>> extract_second_level_domain("news.bbc.co.uk")
        'bbc'
    """
    # 尝试添加默认协议，以确保 urlparse 能正确解析
    if not url.startswith(('http://', 'https://', '//')):
        url = '//' + url # 添加协议，例如 "www.example.com" 变为 "//www.example.com"

    try:
        parsed_url = urlparse(url)
        netloc = parsed_url.netloc

        # 如果没有网络位置（例如输入为空字符串），则无法提取
        if not netloc:
            return None

        # 移除端口号（如果存在）
        if ':' in netloc:
            netloc = netloc.split(':')[0]

        # 移除可能的 www. 等前缀
        if netloc.startswith('www.'):
            netloc = netloc[4:]
        elif netloc.startswith('m.'): # 移动版网站常见
            netloc = netloc[2:]
        elif netloc.startswith('blog.'): # 博客子域名
            netloc = netloc[5:]
        # 可以根据需要添加更多常见的子域名处理

        # 将域名按点分割
        parts = netloc.split('.')
        num_parts = len(parts)

        # 针对不同长度的域名进行判断
        if num_parts >= 2:
            # 考虑常见的顶级域名（TLDs）和二级顶级域名（SLDs）
            # 这是一个简化的列表，实际情况可能更复杂
            # 例如 .co.uk, .com.cn, .org.au 等
            if num_parts >= 3 and parts[-2] in ['co', 'com', 'org', 'net', 'gov', 'edu', 'mil'] \
                                and len(parts[-1]) <= 3: # 简易判断，避免误伤
                # 处理 .co.uk, .com.cn 这类情况
                return parts[-3]
            else:
                # 常见的一级域名，例如 .com, .cn, .io
                return parts[-2]
        else:
            # 少于2个部分，无法构成二级域名（例如 "localhost" 或 "example"）
            return None

    except Exception as e:
        # 捕获解析过程中的异常
        print(f"Error parsing URL '{url}': {e}")
        return None