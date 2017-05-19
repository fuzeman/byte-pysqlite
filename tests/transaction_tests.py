from __future__ import absolute_import, division, print_function

from byte.collection import Collection
from byte.model import Model
from byte.property import Property
import byte.compilers.sqlite
import byte.executors.pysqlite

from hamcrest import *
from pysqlite2 import dbapi2 as sqlite3
import pytest


class User(Model):
    class Options:
        slots = True

    id = Property(int, primary_key=True)

    username = Property(str)
    password = Property(str)


def test_commit():
    """Test transaction is committed correctly."""
    users = Collection(User, 'pysqlite://:memory:?table=users', plugins=[
        byte.compilers.sqlite,
        byte.executors.pysqlite
    ])

    # Create table
    with users.executor.connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE users (
                    id          INTEGER         PRIMARY KEY AUTOINCREMENT NOT NULL,
                    username    VARCHAR(255),
                    password    VARCHAR(255)
                );
            """)

    # Execute multiple queries inside transaction
    with users.transaction():
        users.insert().items({'id': 1, 'username': 'one', 'password': 'alpha'}).execute()
        users.insert().items({'id': 2, 'username': 'one', 'password': 'alpha'}).execute()
        users.insert().items({'id': 3, 'username': 'one', 'password': 'alpha'}).execute()

    # Ensure items were inserted
    assert_that(list(users.all()), has_length(3))

    # Validate executor state
    assert_that(users.executor.transactions, has_length(0))
    assert_that(users.executor.connections.active, equal_to(0))


def test_rollback():
    """Test transaction is committed correctly."""
    users = Collection(User, 'pysqlite://:memory:?table=users', plugins=[
        byte.compilers.sqlite,
        byte.executors.pysqlite
    ])

    # Create table
    with users.executor.connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE users (
                    id          INTEGER         PRIMARY KEY AUTOINCREMENT NOT NULL,
                    username    VARCHAR(255),
                    password    VARCHAR(255)
                );
            """)

    # Insert multiple items (with conflict) inside transaction
    with pytest.raises(sqlite3.IntegrityError):
        with users.transaction():
            users.insert().items({'id': 1, 'username': 'one', 'password': 'alpha'}).execute()
            users.insert().items({'id': 2, 'username': 'one', 'password': 'alpha'}).execute()
            users.insert().items({'id': 1, 'username': 'one', 'password': 'alpha'}).execute()
            users.insert().items({'id': 3, 'username': 'one', 'password': 'alpha'}).execute()

    # Ensure items were inserted
    assert_that(list(users.all()), has_length(0))

    # Validate executor state
    assert_that(users.executor.transactions, has_length(0))
    assert_that(users.executor.connections.active, equal_to(0))


def test_already_inside_transaction():
    """Ensure an exception is raised while attempting to create a transaction while already in a transaction."""
    users = Collection(User, 'pysqlite://:memory:?table=users', plugins=[
        byte.compilers.sqlite,
        byte.executors.pysqlite
    ])

    # Insert multiple items (with conflict) inside transaction
    with pytest.raises(Exception):
        with users.transaction():
            with users.transaction():
                pass
