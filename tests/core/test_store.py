import sqlite3

from core import Store


def get_store() -> Store:
    con = sqlite3.connect(":memory:")
    store = Store("my_store", con)
    return store


def test_set_get():
    store = get_store()
    store.set("lang", ["Python"])
    assert store.get("lang")[0] == "Python"

def test_get_missing():
    store = get_store()
    assert store.get("missing") == None
