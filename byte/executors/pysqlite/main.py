"""byte-pysqlite - executor module."""
from __future__ import absolute_import, division, print_function

from byte.core.plugin.base import Plugin
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


class Base(DatabaseExecutorPlugin):
    """PySQLite base executor class."""

    class Meta(DatabaseExecutorPlugin.Meta):
        """PySQLite base executor metadata."""

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
            self.engine.uri.netloc +
            self.engine.uri.path
        )

        if path == ':memory:':
            return path

        return os.path.abspath(path)

    def construct_compiler(self):
        """Construct compiler."""
        # Find matching compiler
        cls = self.plugins.match(
            Plugin.Kind.Compiler,
            engine=Plugin.Engine.Table,
            extension='sqlite'
        )

        if not cls:
            return None

        # Construct compiler
        self._compiler = cls(self, version=sqlite3.sqlite_version_info)
        return self._compiler

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


class PySqliteDatabaseExecutor(Base):
    """PySQLite database executor class."""

    key = 'database'

    class Meta(Base.Meta):
        """PySQLite database executor metadata."""

        engine = Plugin.Engine.Database

    def open_table(self, table):
        return PySqliteTableExecutor(
            table, self.uri,
            connections=self.connections,
            transactions=self.transactions,
            **self.parameters
        )


class PySqliteTableExecutor(Base):
    """PySQLite table executor class."""

    key = 'table'

    class Meta(Base.Meta):
        """PySQLite table executor metadata."""

        engine = Plugin.Engine.Table
