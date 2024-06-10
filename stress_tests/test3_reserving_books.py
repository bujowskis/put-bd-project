import asyncio
from aiohttp import ClientSession
from utils import send_request, get_books_list


async def send_request_borrow_books(borrower_id, books_isbns):
    async with ClientSession() as session:
        tasks = list()
        for isbn in books_isbns:
            action = 'borrow'
            data = {'isbn': isbn, 'borrowerId': borrower_id}
            task = send_request(session, action, data)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results


if __name__ == '__main__':
    bid1, bid2 = '1', '2'
    event_loop = asyncio.get_event_loop()
    result = event_loop.run_until_complete(get_books_list())
    books = result['result'].split('<br>-')
    books_isbns = list(map(
        lambda x: x.replace('-', '').replace('<br>', '').strip().split(',')[0],
        books
    ))
    tasks = [send_request_borrow_books(bid1, books_isbns), send_request_borrow_books(bid2, books_isbns)]
    results = event_loop.run_until_complete(asyncio.gather(*tasks))

    assert results  # results came back
    for user_results in results:
        for result in user_results:
            print(result)
    event_loop.close()
