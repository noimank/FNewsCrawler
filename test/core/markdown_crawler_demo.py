#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MarkdownCrawler 演示和快速测试脚本
用于展示MarkdownCrawler的主要功能和使用方法
"""

import asyncio
import sys
from pathlib import Path
import time

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fnewscrawler.spiders.core.markdown_crawler import MarkdownCrawler


async def demo_basic_usage():
    """演示基本使用方法"""
    print("\n🔥 演示1: 基本使用方法")
    print("=" * 50)
    
    # 使用上下文管理器（推荐方式）
    async with MarkdownCrawler() as crawler:
        result = await crawler.get_markdown_content(
            "https://finance.eastmoney.com/a/202507233464766684.html",
            content_threshold=0.4,
            use_cache=True
        )
        
        print(f"\n📊 爬取结果:")
        print(f"   成功: {result['success']}")
        print(f"   URL: {result['url']}")
        print(f"   状态码: {result['status_code']}")
        print(f"   清理后Markdown长度: {len(result['markdown'])}")
        print(f"   字数统计: {result['word_count']}")
        
        print(result['markdown'])
        # if result['success'] and result['markdown']:
        #     preview = result['markdown'][:300].replace('\n', ' ')
        #     print(f"\n📝 内容预览:\n{preview}...")
        
        if result['error']:
            print(f"错误信息: {result['error']}")


async def demo_quick_crawl():
    """演示快速爬取方法"""
    print("\n⚡ 演示2: 快速爬取方法")
    print("=" * 50)
    
    # 快速爬取单个URL
    result = await MarkdownCrawler.quick_crawl(
        "https://httpbin.org/json",
        content_threshold=0.3
    )
    
    print(f"\n📊 快速爬取结果:")
    print(f"   成功: {result['success']}")
    print(f"   字数: {result['word_count']}")
    
    if result['success'] and result['markdown']:
        preview = result['markdown'][:200].replace('\n', ' ')
        print(f"   内容预览: {preview}...")


async def demo_batch_crawl():
    """演示批量爬取"""
    print("\n📦 演示3: 批量爬取")
    print("=" * 50)
    
    urls = [
        "https://httpbin.org/html",
        "https://httpbin.org/json",
        "https://httpbin.org/xml",
        "https://httpbin.org/robots.txt"
    ]
    
    start_time = time.time()
    
    async with MarkdownCrawler() as crawler:
        results = await crawler.batch_get_markdown(
            urls,
            max_concurrent=2,
            content_threshold=0.3
        )
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    print(f"批量爬取完成，耗时: {elapsed:.2f}秒")
    print(f"处理URL数: {len(urls)}")
    
    successful_count = 0
    total_words = 0
    
    for i, result in enumerate(results):
        status = "✅" if result['success'] else "❌"
        print(f"   {status} URL {i+1}: {result['word_count']} 字")
        
        if result['success'] and result['markdown']:
            preview = result['markdown'][:100].replace('\n', ' ')
            print(f"      预览: {preview}...")
        
        if result['success']:
            successful_count += 1
            total_words += result['word_count']
        
        if result['error']:
            print(f"    错误: {result['error']}")
    
    print(f"\n📊 统计信息:")
    print(f"  成功率: {successful_count}/{len(urls)} ({successful_count/len(urls)*100:.1f}%)")
    print(f"  总字数: {total_words}")
    print(f"  平均速度: {total_words/elapsed:.0f} 字/秒")


async def demo_singleton_pattern():
    """演示单例模式"""
    print("\n🔄 演示4: 单例模式验证")
    print("=" * 50)
    
    # 创建多个实例
    crawler1 = MarkdownCrawler()
    crawler2 = MarkdownCrawler()
    crawler3 = MarkdownCrawler()
    
    print(f"crawler1 ID: {id(crawler1)}")
    print(f"crawler2 ID: {id(crawler2)}")
    print(f"crawler3 ID: {id(crawler3)}")
    
    print(f"是否为同一实例: {crawler1 is crawler2 is crawler3}")
    
    if crawler1 is crawler2 is crawler3:
        print("✅ 单例模式工作正常")
    else:
        print("❌ 单例模式异常")


async def demo_error_handling():
    """演示错误处理"""
    print("\n🚨 演示5: 错误处理")
    print("=" * 50)
    
    # 测试无效URL
    invalid_urls = [
        "https://this-domain-does-not-exist-12345.com",
        "http://invalid-url",
        "not-a-url"
    ]
    
    async with MarkdownCrawler() as crawler:
        for url in invalid_urls:
            print(f"\n测试无效URL: {url}")
            
            result = await crawler.get_markdown_content(url)
            
            print(f"\n📊 错误处理结果:")
            print(f"   成功: {result['success']}")
            print(f"   错误信息: {result['error']}")
            print(f"   Markdown内容: '{result['markdown']}'")
            print(f"   字数: {result['word_count']}")


async def demo_custom_config():
    """演示自定义配置"""
    print("\n⚙️ 演示6: 自定义配置")
    print("=" * 50)
    
    test_url = "https://httpbin.org/html"
    
    # 不同的配置参数
    configs = [
        {
            "name": "高质量过滤",
            "params": {
                "content_threshold": 0.7,
                "min_word_threshold": 20,
                "exclude_external_links": True
            }
        },
        {
            "name": "宽松过滤",
            "params": {
                "content_threshold": 0.2,
                "min_word_threshold": 5,
                "exclude_external_links": False
            }
        },
        {
            "name": "无缓存模式",
            "params": {
                "use_cache": False,
                "content_threshold": 0.4
            }
        }
    ]
    
    async with MarkdownCrawler() as crawler:
        for config in configs:
            print(f"\n配置: {config['name']}")
            
            result = await crawler.get_markdown_content(
                test_url,
                **config['params']
            )
            
            print(f"\n📊 自定义配置结果:")
            print(f"   成功: {result['success']}")
            print(f"   字数: {result['word_count']}")
            
            if result['success'] and result['markdown']:
                preview = result['markdown'][:150].replace('\n', ' ')
                print(f"   内容预览: {preview}...")


async def demo_performance_comparison():
    """演示性能对比"""
    print("\n🏃 演示7: 性能对比")
    print("=" * 50)
    
    test_urls = [
        "https://httpbin.org/html",
        "https://httpbin.org/json",
        "https://httpbin.org/xml"
    ]
    
    # 测试1: 顺序爬取
    print("\n顺序爬取测试:")
    start_time = time.time()
    
    async with MarkdownCrawler() as crawler:
        sequential_results = []
        for url in test_urls:
            result = await crawler.get_markdown_content(url)
            sequential_results.append(result)
    
    sequential_time = time.time() - start_time
    sequential_words = sum(r['word_count'] for r in sequential_results if r['success'])
    
    # 验证财经新闻内容清理
    for result in sequential_results:
        if result['success']:
            # 验证链接已被移除
            assert '[' not in result['markdown'] or '](' not in result['markdown']
    
    # 测试2: 并发爬取
    print("\n并发爬取测试:")
    start_time = time.time()
    
    async with MarkdownCrawler() as crawler:
        concurrent_results = await crawler.batch_get_markdown(
            test_urls,
            max_concurrent=3
        )
    
    concurrent_time = time.time() - start_time
    concurrent_words = sum(r['word_count'] for r in concurrent_results if r['success'])
    
    # 验证并发结果的财经新闻清理
    for result in concurrent_results:
        if result['success']:
            assert '[' not in result['markdown'] or '](' not in result['markdown']
    
    print(f"\n📊 性能对比结果:")
    print(f"  顺序爬取: {sequential_time:.2f}秒, {sequential_words}字")
    print(f"  并发爬取: {concurrent_time:.2f}秒, {concurrent_words}字")
    if concurrent_time > 0:
        print(f"  性能提升: {sequential_time/concurrent_time:.1f}倍")
    print(f"  ✅ 财经新闻内容清理验证通过（已移除所有链接）")
    
    # 验证结果一致性
    sequential_success = sum(1 for r in sequential_results if r['success'])
    concurrent_success = sum(1 for r in concurrent_results if r['success'])
    
    print(f"  顺序爬取成功数: {sequential_success}/{len(test_urls)}")
    print(f"  并发爬取成功数: {concurrent_success}/{len(test_urls)}")
    
    # 验证结果一致性
    print("\n📊 结果一致性验证:")
    for i, (seq_result, conc_result) in enumerate(zip(sequential_results, concurrent_results)):
        seq_success = seq_result['success']
        conc_success = conc_result['success']
        print(f"   URL {i+1}: 顺序={seq_success}, 并发={conc_success}")
        
        if seq_success and conc_success:
            # 比较内容长度差异
            seq_len = len(seq_result.get('markdown', ''))
            conc_len = len(conc_result.get('markdown', ''))
            diff_percent = abs(seq_len - conc_len) / max(seq_len, conc_len, 1) * 100
            print(f"      内容长度差异: {diff_percent:.1f}%")


async def main():
    """主演示函数"""
    print("🎯 MarkdownCrawler 功能演示")
    print("=" * 60)
    print("这个演示将展示MarkdownCrawler的各种功能和使用方法")
    
    try:
        # 运行所有演示
        await demo_basic_usage()
        await demo_quick_crawl()
        await demo_batch_crawl()
        await demo_singleton_pattern()
        await demo_error_handling()
        await demo_custom_config()
        await demo_performance_comparison()
        
        print("\n🎉 所有演示完成！")
        print("\n💡 使用提示:")
        print("  1. 推荐使用 'async with MarkdownCrawler() as crawler' 语法")
        print("  2. 批量爬取时注意控制并发数，避免对目标网站造成压力")
        print("  3. 根据需要调整 content_threshold 参数来控制内容质量")
        print("  4. 启用缓存可以显著提升重复请求的性能")
        print("  5. 处理财经新闻时，建议设置合适的 excluded_tags")
        
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        print("请检查网络连接和依赖库是否正确安装")


if __name__ == "__main__":
    print("启动MarkdownCrawler演示...")
    asyncio.run(main())