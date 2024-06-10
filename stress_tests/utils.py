import random
import sys
from string import ascii_letters
from aiohttp import ClientSession
from aiohttp.client_exceptions import ContentTypeError


url, headers = 'http://127.0.0.1:8089/process', {'Content-Type': 'application/json'}


async def send_request(session: ClientSession, action: str, data):
    async with session.post(url=url, headers=headers, json={'action': action, **data}) as response:
        # return await response.json()
        try:
            return await response.json()
        except ContentTypeError as e:
            # Log the error and the response text for debugging
            text = await response.text()
            print(f"ContentTypeError: {e}\nResponse text: {text}")
            sys.exit()


def generate_random_string():
    return ''.join(random.choice(ascii_letters) for _ in range(10))


def generate_random_year():
    return random.randint(1800, 2024)


def generate_random_borrower_id():
    return random.randint(1000, 9999)


def generate_random_isbn():
    return str(random.randint(1, 999_999_999_999))  # potentially problematic on conflict


def generate_random_data(action: str):
    return {
        'action': action,
        'isbn': generate_random_isbn(),
        'title': generate_random_string(),
        'author': generate_random_string(),
        'yearOfPublication': generate_random_year(),
        'publisher': generate_random_string(),
        'borrowerId': generate_random_borrower_id()
    }


async def get_books_list():
    async with ClientSession() as session:
        async with session.post(url, headers=headers, json={'action': 'list'}) as response:
            result = await response.json()
            return result


async def check_booking_status(data):
    async with ClientSession() as session:
        async with session.post(url, headers=headers, json={'action': 'info', **data}) as response:
            result = await response.json()
            print("\nbooking status")
            for i in result['result'].split('<br>'):
                print(i)
