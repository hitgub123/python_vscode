import asyncio

async def crawl1():
    print("Crawl1: Starting")
    await asyncio.sleep(2)  # 模拟 I/O 操作
    print("Crawl1: Done")

async def crawl2():
    print("Crawl2: Starting")
    await asyncio.sleep(1)  # 模拟 I/O 操作
    print("Crawl2: Done")

async def main():
    await asyncio.gather(crawl1(), crawl2())  # 并发运行

if __name__ == "__main__":
    # 同步执行
    asyncio.run(crawl1())
    asyncio.run(crawl2())
    asyncio.run(main())