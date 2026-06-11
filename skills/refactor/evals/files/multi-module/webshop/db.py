"""Naive in-memory storage shared by the whole app."""

_TABLES = {"users": {}, "products": {}, "orders": {}}
_SEQ = {"users": 0, "products": 0, "orders": 0}


def next_id(table):
    _SEQ[table] += 1
    return _SEQ[table]


def save(table, record):
    _TABLES[table][record["id"]] = record
    return record


def find(table, record_id):
    return _TABLES[table].get(record_id)


def all_records(table):
    return list(_TABLES[table].values())


def clear():
    for table in _TABLES.values():
        table.clear()
    for key in _SEQ:
        _SEQ[key] = 0
