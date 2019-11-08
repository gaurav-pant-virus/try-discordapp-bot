import sqlite3
import os

class Database(object):
    def __init__(self):
        self.connection = sqlite3.connect(os.getenv('SQLITE_DB'))
        self.cursor = self.connection.cursor()
        self._create_db()

    def _create_db(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER primary key AUTOINCREMENT,
            timestamp datetime default CURRENT_TIMESTAMP,
            query text
            )'''
        )

    def __enter__(self):
        return self

    def __exit__(self, ext_type, exc_value, traceback):
        self.cursor.close()
        if isinstance(exc_value, Exception):
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()


class PersistantMixin(object):
    def store_data(self, data):
        with Database() as db:
            db.cursor.execute(
                'INSERT INTO search_history("query") VALUES (?)',
                (data,)
            )
            db.connection.commit()

    def search(self, filter_term):
        with Database() as db:
            db.cursor.execute(
                '''SELECT distinct(query) FROM  search_history WHERE query LIKE ? ORDER BY timestamp'''
                , ('%'+filter_term+'%',)
            )
            return [query[0] for query in db.cursor.fetchall()]
