from fnewscrawler.utils import extract_second_level_domain


def test_1():
    # 常见的网址
    print(f"'https://www.google.com': {extract_second_level_domain('https://www.google.com')}")
    print(f"'http://blog.example.com.cn': {extract_second_level_domain('http://blog.example.com.cn')}")
    print(f"'sub.domain.co.uk': {extract_second_level_domain('sub.domain.co.uk')}")
    print(f"'docs.microsoft.com': {extract_second_level_domain('docs.microsoft.com')}")
    print(f"'baidu.com': {extract_second_level_domain('baidu.com')}")
    print(f"'news.bbc.co.uk': {extract_second_level_domain('news.bbc.co.uk')}")
    print(f"'localhost:8080': {extract_second_level_domain('localhost:8080')}")

    # 边缘情况
    print(f"'' (empty string): {extract_second_level_domain('')}")
    print(f"'invalid-url': {extract_second_level_domain('invalid-url')}")
    print(f"'justdomain': {extract_second_level_domain('justdomain')}")
    print(f"'my.app': {extract_second_level_domain('my.app')}")  # 可能误判
    print(
        f"'www.some-domain.com:8080/path?query': {extract_second_level_domain('www.some-domain.com:8080/path?query')}")

if __name__ == '__main__':
    test_1()
