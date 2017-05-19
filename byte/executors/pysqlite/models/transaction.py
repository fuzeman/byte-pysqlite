"""byte-pysqlite - executor transaction module."""
from __future__ import absolute_import, division, print_function

from byte.executors.core.models.database import DatabaseTransaction
from byte.executors.pysqlite.models.cursor import PySqliteCursor


class PySqliteTransaction(DatabaseTransaction, PySqliteCursor):
    """PySQLite transaction class."""

    def begin(self):
        """Begin transaction."""
        self.instance.execute('BEGIN;')

    def commit(self):
        """Commit transaction."""
        self.connection.instance.commit()

    def rollback(self):
        """Rollback transaction."""
        self.connection.instance.rollback()

    def close(self):
        """Close transaction."""
        # Close cursor
        self.instance.close()
        self.instance = None

        # Close transaction
        super(PySqliteTransaction, self).close()
