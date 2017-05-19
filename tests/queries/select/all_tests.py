from __future__ import absolute_import, division, print_function

from byte.collection import Collection
from byte.model import Model
from byte.property import Property
import byte.compilers.sqlite
import byte.executors.pysqlite

from hamcrest import *


class User(Model):
    class Options:
        slots = True

    id = Property(int, primary_key=True)

    username = Property(str)
    password = Property(str)


def test_all():
    """Test all items can be retrieved from database."""
    users = Collection(User, 'pysqlite://:memory:?table=users', plugins=[
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

            cursor.execute("INSERT INTO users (username, password) VALUES ('one', 'alpha');")
            cursor.execute("INSERT INTO users (username, password) VALUES ('two', 'beta');")
            cursor.execute("INSERT INTO users (username, password) VALUES ('three', 'charlie');")

    # Validate items
    assert_that(users.all(), only_contains(
        has_properties({
            'username': 'one',
            'password': 'alpha'
        }),
        has_properties({
            'username': 'two',
            'password': 'beta'
        }),
        has_properties({
            'username': 'three',
            'password': 'charlie'
        })
    ))
