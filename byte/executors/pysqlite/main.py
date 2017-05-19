"""byte-pysqlite - executor module."""
from __future__ import absolute_import, division, print_function

from byte.executors.core.base import DatabaseExecutorPlugin
from byte.executors.pysqlite.models.connection import PySqliteConnection
from byte.executors.pysqlite.models.cursor import PySqliteCursor
from byte.executors.pysqlite.models.transaction import PySqliteTransaction
from byte.executors.pysqlite.tasks import PySqliteInsertTask, PySqliteSelectTask
from byte.queries import InsertQuery, SelectQuery

from pysqlite2 import dbapi2 as sqlite3
import logging
import os

log = logging.getLogger(__name__)


class PySqliteExecutor(DatabaseExecutorPlugin):
    """PySQLite executor class."""

    key = 'pysqlite'

    class Meta(DatabaseExecutorPlugin.Meta):
        """PySQLite executor metadata."""

        content_type = 'application/x-sqlite3'

        extension = [
            'db',
            'sqlite'
        ]

        scheme = [
            'pysqlite',
            'sqlite'
        ]

    @property
    def path(self):
        """Retrieve database path.

        :return: Database Path
        :rtype: str
        """
        path = (
            self.collection.uri.netloc +
            self.collection.uri.path
        )

        if path == ':memory:':
            return path

        return os.path.abspath(path)

    def construct_compiler(self):
        """Construct compiler."""
        return self.plugins.get_compiler('sqlite')(
            self,
            version=sqlite3.sqlite_version_info
        )

    def create_connection(self):
        """Connect to database.

        :return: SQLite Connection
        :rtype: sqlite3.Connection
        """
        # Connect to database
        instance = sqlite3.connect(self.path)
        instance.isolation_level = None

        # Create connection
        connection = PySqliteConnection(self, instance)

        # Configure connection
        with connection.transaction() as transaction:
            # Enable write-ahead logging
            transaction.execute('PRAGMA journal_mode=WAL;')

        return connection

    def create_transaction(self, connection=None):
        """Create database transaction.

        :return: SQLite Connection
        :rtype: sqlite3.Connection
        """
        return PySqliteTransaction(
            self,
            connection=connection
        )

    def cursor(self, connection=None):
        """Create database cursor.

        :return: Cursor
        :rtype: byte.executors.sqlite.models.cursor.SqliteCursor
        """
        return PySqliteCursor(
            self,
            connection=connection
        )

    def execute(self, query):
        """Execute query.

        :param query: Query
        :type query: byte.queries.Query
        """
        statements = self.compiler.compile(query)

        if not statements:
            raise ValueError('No statements returned from compiler')

        # Construct task
        if isinstance(query, SelectQuery):
            return PySqliteSelectTask(self, statements).execute()

        if isinstance(query, InsertQuery):
            return PySqliteInsertTask(self, statements).execute()

        raise NotImplementedError('Unsupported query: %s' % (type(query).__name__,))
