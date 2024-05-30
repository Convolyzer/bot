import sqlite3
import json


class Store:
    def __init__(self, name, con: sqlite3.Connection) -> None:
        """Create or load a store.
        - name is the table name used by the store
        - con is the sqlite3 connection
        """
        self.__con = con
        self.__table_name = name
        cursor = con.cursor()
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {name} (
                key STRING PRIMARY KEY,
                value STRING NOT NULL
            );
            """
        )
        cursor.close()

    def set(self, key: str, value):
        """Set the specified value for this key in the store.
        The value is an object that will be serialised and stored in a json format.
        """
        data = json.dumps(value)
        cursor = self.__con.cursor()
        cursor.execute(
            f"""
            REPLACE INTO {self.__table_name} (key, value)
            VALUES ('{key}', '{data}')
            """
        )
        self.__con.commit()
        cursor.close()

    def get(self, key: str):
        """Return the value with this key in the store"""
        cursor = self.__con.cursor()
        res = cursor.execute(
            f"""
            SELECT value FROM {self.__table_name}
            WHERE key = '{key}'
            """
        )
        value = res.fetchone()
        if value is None:
            return None
        js = json.loads(value[0])
        cursor.close()
        return js
