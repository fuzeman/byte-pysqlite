from __future__ import absolute_import, division, print_function

from byte.table import Model, Property, Table
import byte.compilers.sqlite
import byte.executors.pysqlite

from hamcrest import *


class User(Model):
    class Options:
        slots = True

    id = Property(int, primary_key=True)

    username = Property(str)
    password = Property(str)


def test_or():
    """Test OR expression inside string can be compiled and executed."""
    users = Table(User, 'pysqlite://:memory:', name='users', plugins=[
        byte.compilers.sqlite,
        byte.executors.pysqlite
    ])

    # Create table, and add items directly to database
    with users.executor.connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE users (
                    id          INTEGER         PRIMARY KEY AUTOINCREMENT NOT NULL,
                    username    VARCHAR(255),
                    password    VARCHAR(255)
                );
            """)

            cursor.execute("INSERT INTO users (id, username, password) VALUES (1, 'one', 'alpha');")
            cursor.execute("INSERT INTO users (id, username, password) VALUES (2, 'two', 'beta');")
            cursor.execute("INSERT INTO users (id, username, password) VALUES (3, 'three', 'charlie');")

    # Validate items
    users = list(users.select().where('username == "one" or password == "charlie"').execute())

    assert_that(users, has_length(2))


def test_and():
    """Test AND expression inside string can be compiled and executed."""
    users = Table(User, 'pysqlite://:memory:', name='users', plugins=[
        byte.compilers.sqlite,
        byte.executors.pysqlite
    ])

    # Create table, and add items directly to database
    with users.executor.connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE users (
                    id          INTEGER         PRIMARY KEY AUTOINCREMENT NOT NULL,
                    username    VARCHAR(255),
                    password    VARCHAR(255)
                );
            """)

            cursor.execute("INSERT INTO users (id, username, password) VALUES (1, 'one', 'alpha');")
            cursor.execute("INSERT INTO users (id, username, password) VALUES (2, 'two', 'beta');")
            cursor.execute("INSERT INTO users (id, username, password) VALUES (3, 'three', 'charlie');")

    # Validate items
    users = list(users.select().where('id > 1 and password != ?', 'charlie').execute())

    assert_that(users, has_length(1))
