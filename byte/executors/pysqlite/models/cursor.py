"""byte-pysqlite - executor cursor module."""
from __future__ import absolute_import, division, print_function

from byte.executors.core.models.database import DatabaseCursor

import logging

log = logging.getLogger(__name__)


class PySqliteCursor(DatabaseCursor):
    """SQLite cursor class."""

    def __init__(self, executor, connection=None):
        """Create SQLite Cursor.

        :param executor: Executor
        :type executor: byte.executors.core.base.Executor

        :param connection: Connection
        :type connection: byte.executors.core.models.database.connection.Connection or None
        """
        super(PySqliteCursor, self).__init__(executor, connection=connection)

        # Create cursor
        self.instance = self.connection.instance.cursor()

    @property
    def columns(self):
        """Retrieve columns description from cursor."""
        return self.instance.description

    def execute(self, statement, parameters=None):
        """Execute statement."""
        log.debug('Execute: %r %r', statement, parameters)

        if not parameters:
            return self.instance.execute(statement)

        return self.instance.execute(statement, parameters)

    def close(self):
        """Close cursor."""
        super(PySqliteCursor, self).close()

        # Close cursor
        self.instance.close()
        self.instance = None

    def __iter__(self):
        return iter(self.instance)
