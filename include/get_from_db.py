import sqlite3


# getting label names and rowids
def get_label_names(database):
    database = sqlite3.connect(f'databases/{database}.db')
    db = database.cursor()
    db.execute("SELECT label_name, ROWID FROM Labels ORDER BY priority")
    items = db.fetchall()
    database.close()
    return items
