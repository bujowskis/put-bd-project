from aiohttp import ClientSession
from utils import send_request, generate_random_data
import random
import asyncio


async def send_requests_from_client_id(client_id):
    async with ClientSession() as session:
        actions, number_of_requests = ['add', 'remove', 'info', 'borrow', 'return'], 128
        tasks = []
        for _ in range(number_of_requests):
            action = random.choice(actions)
            print(client_id, action)
            data = generate_random_data(action)
            task = send_request(session, action, data)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results


if __name__ == '__main__':
    clients = ['client1', 'client2', 'client3']

    event_loop = asyncio.get_event_loop()
    tasks = list()
    for client_id in clients:
        task = send_requests_from_client_id(client_id)
        tasks.append(task)
    results = event_loop.run_until_complete(asyncio.gather(*tasks))

    assert results  # the results came back
    event_loop.close()
