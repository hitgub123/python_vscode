import asyncio, time
from crawl4ai import *


async def crawl_one():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://novel.tingroom.com/duanpian/4794/123235.html",
        )
        with open(f"doc/crawl4AI/{time.time()}.md", "w", encoding="utf-8") as f:
            f.write(result.markdown)


async def crawl_many():
    urls = [
        "https://novel.tingroom.com/duanpian/4794/123238.html",
        "https://novel.tingroom.com/duanpian/4794/123236.html",
        "https://novel.tingroom.com/duanpian/4794/123237.html",
    ]
    config = CrawlerRunConfig(
        stream=True, cache_mode=CacheMode.BYPASS  # Enable streaming mode
    )
    async with AsyncWebCrawler() as crawler:
        async for result in await crawler.arun_many(urls=urls, config=config):
            if result.success:
                print(f"Just completed: {result.url}")
                with open(f"doc/crawl4AI/{time.time()}.html", "w", encoding="utf-8") as f:
                    f.write(result.html)


if __name__ == "__main__":
    # asyncio.run(crawl_one())
    asyncio.run(crawl_many())