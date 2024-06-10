import asyncio
from aiohttp import ClientSession
from utils import send_request, check_booking_status


async def stress_test(action: str, data, number_of_requests: int, borrowerId):
    async with ClientSession() as session:
        tasks = list()
        for _ in range(number_of_requests):
            data['borrowerId'] = f'{borrowerId}'
            task = send_request(session, action, data)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results


if __name__ == '__main__':
    bid1, bid2 = 1, 2
    action, data = 'borrow', {'isbn': '0140291784'}
    num_requests = 256

    event_loop = asyncio.get_event_loop()
    results = event_loop.run_until_complete(
        asyncio.gather(
            stress_test(action, data, num_requests, bid1),
            stress_test(action, data, num_requests, bid2)
        )
    )

    assert results  # results came back
    result = event_loop.run_until_complete(check_booking_status({'isbn': data['isbn']}))
    event_loop.close()
