from cassandra.cluster import Session


table_name = 'books'


def add_new_book(
    session: Session,
    isbn: str,
    title: str,
    author: str,
    year_of_publication: str,
    publisher: str
):
    # check if book already exists
    result = session.execute(f"SELECT isbn FROM {table_name} WHERE isbn = %s;", [isbn])
    if result:
        return "Book with this ISBN already exists"

    # prepare and insert book to database
    new_book_info = {
        'isbn': isbn,
        'book_title': title.strip().replace("'", "''"),  # apostrophe may mess with SQL
        'book_author': author,
        'year_of_publication': int(year_of_publication),
        'publisher': publisher,
        'borrower_id': -1
    }
    session.execute(
        f"INSERT INTO {table_name} ({','.join(list(new_book_info.keys()))})" +
        f"VALUES ({','.join(['%s']  * len(new_book_info))})",
        new_book_info.values()
    )
    return f'Added new book<br><br>{get_book_info(session, isbn)}'


def remove_book(session: Session, isbn: str):
    result = session.execute(
        f"DELETE FROM {table_name} WHERE isbn = %s IF EXISTS;",
        [isbn]
    )
    if result.one().applied:
        return f'Deleted book with ISBN: {isbn}'
    else:
        return f'Book with ISBN: {isbn} does not exist'


def get_book_info(session: Session, isbn: str):
    result = session.execute(
        f"SELECT * FROM {table_name} WHERE isbn = %s;",
        [isbn]
    )
    if result:
        output, row = "", next(iter(result))
        for column_name in row._fields:
            column_value = getattr(row, column_name)
            if column_name == "borrower_id":
                # map -1 into human-readable message
                mapped_column_value = '(not borrowed)' if column_value == -1 else column_value
                output += "{: >25} {: >25}<br>".format(column_name, mapped_column_value)
                continue
            # map column name into human-friendly looks
            mapped_column_name = column_name.replace('_', ' ')
            output += "{: >25} {: >25}<br>".format(mapped_column_name, column_value)
        return output
    else:
        return f'Book with ISBN: {isbn} does not exist'


def borrow_book(session: Session, isbn: str, borrower_id: str):
    result = session.execute(
        f"SELECT borrower_id FROM {table_name} WHERE isbn = %s;",
        [isbn]
    )
    if not result:
        return f'Book with ISBN: {isbn} does not exist'

    result = list(next(iter(result)))[0]
    if result != -1:
        return f"Book with ISBN: {isbn} is already borrowed"

    session.execute(
        f"UPDATE {table_name} " +
        f"SET borrower_id = %s " +
        f"WHERE isbn = %s;",
        [int(borrower_id), isbn]
    )
    return f'Borrowed book with ISBN: {isbn} <br><br>{get_book_info(session, isbn)}'


def return_book(session: Session, isbn: str):
    result = session.execute(
        f"SELECT borrower_id FROM {table_name} WHERE isbn = %s;",
        [isbn]
    )
    if not result:
        return f'Book with ISBN: {isbn} does not exist'

    result = list(next(iter(result)))[0]
    if result == -1:
        return f"Book with ISBN: {isbn} is not borrowed"

    session.execute(
        f"UPDATE {table_name} " +
        f"SET borrower_id = %s " +
        f"WHERE isbn = %s;",
        [-1, isbn]
    )
    return f'Returned book with ISBN: {isbn}<br><br>{get_book_info(session, isbn)}'


def get_list_of_books(session: Session):
    result = list(session.execute(f"SELECT isbn, book_title FROM {table_name} limit 1024;"))
    return_string = ""
    for book in result:
        return_string += f"- {str(book.isbn)}, {str(book.book_title)} <br>"
    return return_string
