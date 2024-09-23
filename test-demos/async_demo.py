import asyncio


async def fetch_data():
    print("开始获取数据...")
    await asyncio.sleep(2)  # 模拟IO操作
    print("数据获取完成")
    return {"data": 123}


async def main():
    result = await fetch_data()
    print(result)


asyncio.run(main())
