import asyncio
from typing import Optional, Dict, Any

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

from fnewscrawler.utils.logger import LOGGER


class MarkdownCrawler:
    """
    高性能单例模式的Markdown内容爬取器
    专门用于获取指定URL的内容并返回Markdown格式
    基于Crawl4AI库实现，支持异步操作和智能内容过滤
    """
    
    _instance: Optional['MarkdownCrawler'] = None
    _crawler: Optional[AsyncWebCrawler] = None
    _initialized: bool = False
    _lock = asyncio.Lock()
    
    def __new__(cls) -> 'MarkdownCrawler':
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(MarkdownCrawler, cls).__new__(cls)
        return cls._instance
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self._initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self._cleanup()
    
    async def _initialize(self) -> None:
        """初始化爬虫实例（线程安全）"""
        async with self._lock:
            if not self._initialized:
                try:
                    # 配置浏览器参数以获得最佳性能
                    browser_config = BrowserConfig(
                        headless=True,  # 无头模式提升性能
                        verbose=False,  # 减少日志输出
                        extra_args=[
                            '--no-sandbox',
                            '--disable-dev-shm-usage',
                            '--disable-gpu',
                            '--disable-web-security',
                            '--disable-features=VizDisplayCompositor',
                            '--disable-background-timer-throttling',
                            '--disable-renderer-backgrounding',
                            '--disable-backgrounding-occluded-windows'
                        ]
                    )
                    
                    # 创建爬虫实例
                    self._crawler = AsyncWebCrawler(config=browser_config)
                    await self._crawler.__aenter__()
                    
                    self._initialized = True
                    LOGGER.info("MarkdownCrawler 初始化完成")
                    
                except Exception as e:
                    LOGGER.error(f"MarkdownCrawler 初始化失败: {e}")
                    raise
    
    async def _cleanup(self) -> None:
        """清理资源"""
        if self._crawler and self._initialized:
            try:
                await self._crawler.__aexit__(None, None, None)
                self._crawler = None
                self._initialized = False
                LOGGER.info("MarkdownCrawler 资源清理完成")
            except Exception as e:
                LOGGER.error(f"MarkdownCrawler 资源清理失败: {e}")
    
    async def get_markdown_content(
        self, 
        url: str, 
        *,
        use_cache: bool = True,
        content_threshold: float = 0.6,
        min_word_threshold: int = 20,
        word_count_threshold: int = 10,
        excluded_tags: Optional[list] = None,
        exclude_external_links: bool = True,
        exclude_social_media_links: bool = True,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        获取指定URL的财经新闻Markdown内容
        专门针对财经新闻优化，过滤链接和无关内容
        
        Args:
            url: 目标URL
            use_cache: 是否使用缓存（默认True，提升性能）
            content_threshold: 内容过滤阈值（0-1，越高过滤越严格，财经新闻建议0.6）
            min_word_threshold: 最小单词数阈值（财经新闻建议20）
            word_count_threshold: 单词计数阈值（财经新闻建议10）
            excluded_tags: 排除的HTML标签列表
            exclude_external_links: 是否排除外部链接
            exclude_social_media_links: 是否排除社交媒体链接
            custom_config: 自定义配置字典
            
        Returns:
            包含清理后Markdown内容的字典
            {
                'success': bool,
                'url': str,
                'markdown': str,  # 清理后的markdown内容，无链接
                'word_count': int,
                'status_code': int,
                'error': str or None
            }
        """
        if not self._initialized:
            await self._initialize()
        
        # 财经新闻专用标签过滤列表
        if excluded_tags is None:
            excluded_tags = [
                'script', 'style', 'nav', 'footer', 'header', 'aside',
                'advertisement', 'ads', 'sidebar', 'menu', 'breadcrumb',
                'social-share', 'comment', 'related-articles', 'popup'
            ]
        
        try:
            # 配置财经新闻专用内容过滤器
            content_filter = PruningContentFilter(
                threshold=content_threshold,
                threshold_type="fixed",
                min_word_threshold=min_word_threshold
            )
            
            # 配置Markdown生成器 - 专门为财经新闻优化
            markdown_generator = DefaultMarkdownGenerator(
                content_filter=content_filter,
                options={
                    "ignore_links": True,  # 财经新闻不需要链接
                    "ignore_images": True,  # 财经新闻主要关注文本内容
                    "body_only": True,
                    "include_raw_html": False
                }
            )
            
            # 配置爬取参数 - 针对财经新闻优化
            crawler_config = CrawlerRunConfig(
                cache_mode=CacheMode.ENABLED if use_cache else CacheMode.BYPASS,
                markdown_generator=markdown_generator,
                word_count_threshold=word_count_threshold,
                excluded_tags=excluded_tags,
                exclude_external_links=exclude_external_links,
                exclude_social_media_links=exclude_social_media_links,
                remove_overlay_elements=True,  # 移除弹窗等覆盖元素
                **(custom_config or {})
            )
            
            LOGGER.info(f"开始爬取URL: {url}")
            
            # 执行爬取
            result = await self._crawler.arun(
                url=url,
                config=crawler_config
            )
            # 处理结果 - 只返回清理后的markdown
            if result.success:
                # 优先使用fit_markdown，如果为空则使用raw_markdown
                cleaned_markdown = ''
                if result.markdown:
                    if result.markdown.fit_markdown:
                        cleaned_markdown = result.markdown.fit_markdown
                    elif result.markdown.raw_markdown:
                        cleaned_markdown = result.markdown.raw_markdown
                
                # 进一步清理财经新闻中的垃圾内容
                cleaned_markdown = self._clean_financial_content(cleaned_markdown)
                
                response_data = {
                    'success': True,
                    'url': url,
                    'markdown': cleaned_markdown,
                    'word_count': len(cleaned_markdown.split()) if cleaned_markdown else 0,
                    'status_code': result.status_code,
                    'error': None
                }
                
                LOGGER.info(f"财经新闻爬取成功: {url}, 字数: {response_data['word_count']}")
                return response_data
            else:
                error_msg = f"爬取失败: {result.error_message if hasattr(result, 'error_message') else '未知错误'}"
                LOGGER.error(error_msg)
                return {
                    'success': False,
                    'url': url,
                    'markdown': '',
                    'word_count': 0,
                    'status_code': getattr(result, 'status_code', 0),
                    'error': error_msg
                }
                
        except Exception as e:
            error_msg = f"爬取过程中发生异常: {str(e)}"
            LOGGER.error(error_msg)
            return {
                'success': False,
                'url': url,
                'markdown': '',
                'word_count': 0,
                'status_code': 0,
                'error': error_msg
            }
    
    def _clean_financial_content(self, markdown: str) -> str:
        """
        清理财经新闻内容中的垃圾信息
        
        Args:
            markdown: 原始markdown内容
            
        Returns:
            清理后的markdown内容
        """
        if not markdown:
            return ''
        
        import re
        
        # 移除所有链接（包括内联链接和引用链接）
        markdown = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', markdown)
        markdown = re.sub(r'\[([^\]]+)\]\[[^\]]*\]', r'\1', markdown)
        
        # 移除图片引用
        markdown = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', markdown)
        
        # 移除HTML标签残留
        markdown = re.sub(r'<[^>]+>', '', markdown)
        
        # 移除多余的空行（保留段落结构）
        markdown = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown)
        
        # 移除行首行尾空白
        lines = [line.strip() for line in markdown.split('\n')]
        markdown = '\n'.join(lines)
        
        # 移除常见的财经网站垃圾文本
        junk_patterns = [
            r'点击.*?查看.*?',
            r'更多.*?资讯.*?',
            r'关注.*?微信.*?',
            r'扫码.*?下载.*?',
            r'免责声明.*?',
            r'风险提示.*?',
            r'投资有风险.*?',
            r'本文.*?不构成.*?建议.*?',
            r'.*?客服.*?电话.*?',
            r'.*?版权所有.*?',
        ]
        
        for pattern in junk_patterns:
            markdown = re.sub(pattern, '', markdown, flags=re.IGNORECASE)
        
        # 最终清理多余空行
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)
        
        return markdown.strip()
    
    async def batch_get_markdown(
        self, 
        urls: list[str], 
        *,
        max_concurrent: int = 5,
        **kwargs
    ) -> list[Dict[str, Any]]:
        """
        批量获取多个URL的Markdown内容
        
        Args:
            urls: URL列表
            max_concurrent: 最大并发数（默认5，避免过载）
            **kwargs: 传递给get_markdown_content的其他参数
            
        Returns:
            结果列表，每个元素对应一个URL的处理结果
        """
        if not self._initialized:
            await self._initialize()
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_url(url: str) -> Dict[str, Any]:
            async with semaphore:
                return await self.get_markdown_content(url, **kwargs)
        
        LOGGER.info(f"开始批量爬取 {len(urls)} 个URL，最大并发数: {max_concurrent}")
        
        tasks = [process_url(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'success': False,
                    'url': urls[i],
                    'markdown': '',
                    'word_count': 0,
                    'status_code': 0,
                    'error': str(result)
                })
            else:
                processed_results.append(result)
        
        successful_count = sum(1 for r in processed_results if r['success'])
        LOGGER.info(f"批量爬取完成: {successful_count}/{len(urls)} 成功")
        
        return processed_results
    
    @classmethod
    async def create_instance(cls) -> 'MarkdownCrawler':
        """
        创建并初始化MarkdownCrawler实例的便捷方法
        
        Returns:
            初始化完成的MarkdownCrawler实例
        """
        instance = cls()
        await instance._initialize()
        return instance
    
    @classmethod
    async def quick_crawl(cls, url: str, **kwargs) -> Dict[str, Any]:
        """
        快速爬取单个URL的便捷方法
        
        Args:
            url: 目标URL
            **kwargs: 传递给get_markdown_content的参数
            
        Returns:
            爬取结果字典
        """
        async with cls() as crawler:
            return await crawler.get_markdown_content(url, **kwargs)

