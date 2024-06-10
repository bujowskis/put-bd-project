from utils import send_request, check_booking_status
import asyncio
from aiohttp import ClientSession


async def send_number_of_requests(action: str, data, number_of_requests: int):
    async with ClientSession() as session:
        tasks = list()
        for _ in range(number_of_requests):
            task = send_request(session, action, data)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results


if __name__ == '__main__':
    data = {
        'action': 'add',
        'isbn': '999999999999',
        'title': 'foo_title',
        'author': 'foo_author',
        'yearOfPublication': 12345,
        'publisher': 'foo_publisher',
        'borrowerId': 1234
    }
    number_of_requests = 128

    event_loop = asyncio.get_event_loop()
    results = event_loop.run_until_complete(send_number_of_requests(data['action'], data, number_of_requests))

    assert results  # the results came back
    for result in results:
        print(result)
    event_loop.run_until_complete(check_booking_status({'isbn': data['isbn']}))
    event_loop.close()
