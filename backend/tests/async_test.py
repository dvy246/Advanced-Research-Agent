import asyncio
import time 


async def fetch(times):
    print(f'doing task with{times}')
    time.sleep(times)
    asyncio.sleep(times)
    print('done with the task')

async def main():
    start=time.perf_counter()
    task1=asyncio.create_task(fetch(100000000000000000000))
    task2=asyncio.create_task(fetch(3))
    asyncio.sleep(5)
    resul1=await task1
    resul2=await task2
    print(resul1,resul2)
    end=time.perf_counter()
    print(end-start)

asyncio.run(main())