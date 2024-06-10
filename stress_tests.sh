#!/bin/bash
cd stress_tests

echo 'test1_many_add.py'
python3 test1_many_add.py

echo 'test2_multiple_actions_and_clients.py'
python3 test2_multiple_actions_and_clients.py

echo 'test3_reserving_books.py'
python3 test3_reserving_books.py

echo 'test4_borrow_and_return.py'
python3 test4_borrow_and_return.py

echo 'test5_conflicting_reservation.py'
python3 test5_conflicting_reservation.py