"""byte-pysqlite - executor connection module."""
from __future__ import absolute_import, division, print_function

from byte.executors.core.models.database import DatabaseConnection


class PySqliteConnection(DatabaseConnection):
    """SQLite connection class."""

    def __init__(self, executor, instance):
        """Create sqlite connection.

        :param executor: Executor
        :type executor: byte.executors.core.base.Executor

        :param instance: SQLite Connection
        :type instance: sqlite3.Connection
        """
        super(PySqliteConnection, self).__init__(executor)

        self.instance = instance
