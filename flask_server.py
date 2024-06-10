from cassandra.cluster import Cluster
from flask import Flask, request, render_template, jsonify
import threading
from bookkeeper_functions import add_new_book, remove_book, get_book_info, borrow_book, return_book, get_list_of_books


cluster = Cluster(['c1', 'c2', 'c3'])
session = cluster.connect()
session.execute(f'USE bookkeeper')
webpage_name = 'bookkeeper.html'
app = Flask(__name__)


@app.route('/process', methods=['POST'])
def process():
    request_data = request.get_json()
    isbn = request_data.get('isbn', '')
    title = request_data.get('title', '')
    author = request_data.get('author', '')
    year_of_publication = request_data.get('yearOfPublication', '')
    publisher = request_data.get('publisher', '')
    borrower_id = request_data.get('borrowerId', '')

    # choose what to do depending on the requested action
    action, result = request_data['action'], None
    if action == 'add':
        if not all([isbn, title, author, year_of_publication, publisher]):
            result = 'Unsuccessful: adding new book requires isbn, title, author, year_of_publication, publisher'
        else:
            result = add_new_book(session, isbn, title, author, year_of_publication, publisher)
    elif action == 'remove':
        if not isbn:
            result = 'Unsuccessful: removing book requires isbn'
        else:
            result = remove_book(session, isbn)
    elif action == 'info':
        if not isbn:
            result = 'Unsuccessful: fetching book info requires isbn'
        else:
            result = get_book_info(session, isbn)
    elif action == 'borrow':
        if not all([isbn, borrower_id]):
            result = 'Unsuccessful: borrowing book requires isbn, borrower_id'
        else:
            result = borrow_book(session, isbn, borrower_id)
    elif action == 'return':
        if not isbn:
            result = 'Unsuccessful: returning book requires isbn'
        else:
            result = return_book(session, isbn)
    elif action == 'list':
        result = get_list_of_books(session)
    return jsonify(result=result)


@app.route('/')
def index():
    # return send_from_directory('', webpage_name)
    return render_template(webpage_name)


def startup_server():
    app.run(
        host='0.0.0.0',  # localhost
        port=8089
    )


if __name__ == '__main__':
    thread = threading.Thread(target=startup_server)
    thread.start()
    thread.join()
