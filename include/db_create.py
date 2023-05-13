import sqlite3

creating_some_data = """
INSERT INTO Labels VALUES (1, TRUE, 'TO DO')
INSERT INTO Labels VALUES (3, FALSE, 'Zakupy')
INSERT INTO Labels VALUES (3, FALSE, 'Obiady')
INSERT INTO Labels VALUES (2, FALSE, 'Studia')

INSERT INTO Notes VALUES (2, 1, '00-00-2000', 'Zrób1 (p1)', NULL);
INSERT INTO Notes VALUES (2, 3, '00-00-0000', 'Zrób2 (p3)', NULL);
INSERT INTO Notes VALUES (2, 3, '00-00-0000', 'Zrób3 (p3)', NULL);
INSERT INTO Notes VALUES (2, 2, '00-00-0000', 'Zrób4 (p2)', NULL);
INSERT INTO Notes VALUES (3, 1, '00-00-0000', 'Zakup1 (p1)', NULL);
INSERT INTO Notes VALUES (3, 2, '00-00-0000', 'Zakup2 (p2)', NULL);
INSERT INTO Notes VALUES (3, 1, '00-00-0000', 'Zakup3 (p1)', NULL);
"""


def create_all_db():
    create_to_do_db()


def create_to_do_db():
    database = sqlite3.connect('databases/to_do.db')
    db = database.cursor()

    db.execute("""CREATE TABLE Labels (
            priority integer,
            id_default boolean,
            label_name text
    )""")

    db.execute("""CREATE TABLE Notes (
            label_id integer,
            priority integer,
            deadline text,
            note text,
            image blob
    )""")

    # db.execute("SELECT rowid FROM Labels")
    # items = db.fetchall()
    # print([i[0] for i in items])

    #INSERT INTO Labels VALUES (2, 'lab21');

    database.commit()
    database.close()

