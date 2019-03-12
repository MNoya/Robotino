import sqlite3

from datetime import datetime

DB_NAME = 'messages.db'


def setup_database():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        creation_sql = "CREATE TABLE messages(date text, message text, user text)"
        c.execute(creation_sql)
        print(creation_sql)
        conn.commit()
        print("Table created!")
    except:
        pass

    conn.close()


def save_message(message, username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    date_now = datetime.now().strftime("%Y-%m-%d")
    print("Saving message for date {}, submitted by {}".format(date_now, username))
    try:
        creation_sql = "INSERT INTO messages('{}', message, user)".format(date_now)
        print(creation_sql)
        c.execute(creation_sql)
        conn.commit()
        print("Message saved: {}".format(message))
    except Exception as e:
        print("Problem saving message: {}".format(e))

    conn.close()
