from utils import send_request
from aiohttp import ClientSession
import asyncio


async def test_frequent_borrow_and_return(borrower_id: int, isbn, number_of_requests: int):
    async with ClientSession() as session:
        borrow_tasks, return_tasks = list(), list()
        for _ in range(number_of_requests):
            borrow_task = send_request(session, 'borrow', {'isbn': isbn, 'borrowerId': borrower_id})
            return_task = send_request(session, 'return', {'isbn': isbn})
            borrow_tasks.append(borrow_task)
            return_tasks.append(return_task)
        results = await asyncio.gather(*borrow_tasks, *return_tasks)
        return results


if __name__ == '__main__':
    isbn, borrower_id, number_of_requests = '0140291784', 1234, 1024

    event_loop = asyncio.get_event_loop()
    task = test_frequent_borrow_and_return(borrower_id, isbn, number_of_requests)
    results = event_loop.run_until_complete(asyncio.gather(task))

    assert results  # results came back
    for result in results:
        print(result)
    event_loop.close()
