# Bookkeeper - Distributed system for library
This README covers all the aspects required in the report for the project

## Team members
- Szymon Bujowski, 148050
- Dominika Plewińska, 151929

## What is Bookkeeper?
It's a distributed system intended for use by libraries.
It helps management and administration by exposing a web interface, used to perform actions on the books.

The system allows for:
- Listing existing books in the system (library)
- Adding new books
- Deleting existing books
- Fetching book info (ISBN, author, title, borrower, publisher, year of publication)
- Borrowing book (by particular borrower)
- Returning borrowed book

## How to run Bookkeeper?
### 1. Build docker image
Note that the following command assumes you're in the directory of the project
```shell
docker build -t my_flask_server:latest .
```

### 2. Start multi-container application
```shell
docker compose up
```

### 3. Access webpage
The default config is for webpage to be exposed at [localhost:80](http://localhost:80)

## Dataset
https://www.kaggle.com/datasets/saurabhbagchi/books-dataset, preprocessed for usage in the project.
Namely:
- `"Image-URL-S";"Image-URL-M";"Image-URL-L"` columns are dropped
- `borrower_id` field is added (initially at random) to specify if a given book is borrowed (and by whom)

### Database schema
Data resides in keyspace `bookkeeper`, table `books`:
```
isbn                : text (PRIMARY KEY)
book_title:         : text
book_author:        : text
year_of_publication : bigint
publisher           : text
borrower_id         : bigint
```
Note that ISBN is of type `text` because of some instances such as:
```
188164961X, Feel Great, Be Beautiful over 40: Inside Tips on How to Look Better, Be Healthier and Slow the Aging Process
```
Where `X` at the end is valid.

## Distributed system setup
The system is a multi-container docker setup with five services,
connected through `cassandra-net` bridge network:
- 3 Cassandra database nodes - `[c1, c2, c3]`
  - each node has a healthcheck that tests if `describe keyspaces` command from Cassandra Query Language works within 5s timeout
    - if so, the node is considered healthy
    - if not, there's a total of 60 retries in 5s intervals
  - each subsequent node depends on the healthcheck of the previous one
    - `c1->c2`, `c2->c3`
    - this ensures that by the time `c3` is up, all nodes are as well
- Flask server
  - 3 replicas for load balancing, exposed and mapped on one port `8089`
  - on startup, the server:
    - 1 - runs `init_db.py` script to initialize the database (populate it with data from `data/dataset.csv`)
    - 2 - exposes Bookkeeper webpage
  - depends on `c3` being healthy
- Nginx web server reverse proxy (middleware orchestrating client-server flow)
  - listens on port `80` (this is how user accesses [localhost:80](http://localhost:80) webpage)
  - has default volume mount
  - depends on Flask server being healthy

The whole sequence of dependencies on health checks ensures proper setup.

## Stress tests
`/stress_tests` directory contains a number of stress tests that can be run once the system is set up using:
```shell
bash stress_tests.sh
```

The tests intend to simulate possible high-load situations the system may encounter:
- `test1_many_add.py` - high load of adding new book
- `test2_multiple_actions_and_clients.py` - high load of various actions coming from multiple clients at the same time
- `test3_reserving_books.py` - high load of reserving books
- `test4_borrow_and_return.py` - high load of subsequent borrow and return requests
- `test5_conflicting_reservation.py` - high load of two clients trying to borrow the same book at the same time

## Encountered problems
We encountered a number of various problems, concerning different parts and aspects of the project:
- Flask requiring `2.2.2+` version of a library it depends on (`werkzeug`), pulling the most recent one, which happened to not work with it anymore
  - A: specify specific version of `werkzeug`
- database initializing before all Cassandra nodes were fully operational
  - A: implement health checks and specify dependencies
- hyphens are special characters in CQL
  - A: special-handling (double quoting - `'->''` when inserting data)
- various issues with ports due to improper nginx config
  - A: a bit of trial and error, resolving issues one by one
- huge RAM usage by Cassandra nodes
  - A: `MAX_HEAP_SIZE` and `HEAP_NEWSIZE` limits
- no validation of id lead to "sql injection" of `-1`, making "borrow" action a "return" action
  - A: validation
- requiring all attributes specified for any operation
  - A: rewrite code to only require what's actually needed
- unable to use `action_scripts.js` or `bookkeeper.css`
  - A: serving of static files with templating of Flask
