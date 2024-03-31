import sqlite3


def create_tables_if_not_exists():

    conn = sqlite3.connect('bot.db')

    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS users(
        userid INTEGER PRIMARY KEY);
    """)
    conn.commit()

    cur.execute("""CREATE TABLE IF NOT EXISTS channels(
        channel_id TEXT PRIMARY KEY,
        channel_name TEXT);
        """)
    conn.commit()

    cur.execute("""CREATE TABLE IF NOT EXISTS subs(
        userid INTEGER,
        channelid TEXT NOT NULL,
        FOREIGN KEY (userid) REFERENCES users (userid) ON DELETE CASCADE,
        FOREIGN KEY (channelid) REFERENCES channels (channel_id) ON DELETE CASCADE,
        UNIQUE (userid, channelid));
    """)
    conn.commit()

    cur.execute("""CREATE TABLE IF NOT EXISTS nginx(
        url TEXT);
    """)
    conn.commit()

    cur.execute("""CREATE TABLE IF NOT EXISTS urls(
        user_id INTEGER,
        message_id TEXT,
        url TEXT,
        PRIMARY KEY(message_id, user_id));
    """)
    conn.commit()

    cur.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    return conn, cur


def insert(table, data):
    try:
        if table == 'urls':
            cur.execute("INSERT INTO {} VALUES(?, ?, ?);".format(table), data)
        elif isinstance(data, tuple):
            cur.execute("INSERT INTO {} VALUES(?, ?);".format(table), data)
        else:
            cur.execute("INSERT INTO {} VALUES(?);".format(table), (data,))
        conn.commit()
    except sqlite3.Error as error:
        print('{} при вставке следующих данных: {}'.format(error, data))


def clear_tables():
    cur.execute("DELETE from users;")
    cur.execute("DELETE from subs;")
    cur.execute("DELETE from channels;")
    conn.commit()


def clear_nginx():
    cur.execute("DELETE from nginx;")
    conn.commit()


def select_all(table):
    cur.execute("SELECT * FROM {};".format(table))
    all_res = cur.fetchall()
    return all_res


# возвращает название канала по его id
def name_by_id(channel_id):
    cur.execute("""SELECT channel_name FROM channels
        WHERE channel_id="{}";""".format(channel_id))
    all_res = cur.fetchall()
    return all_res


# Возвращает список пользователей (chat_id) которые подписанны на данный канал
def all_users(channel_id):
    cur.execute("""SELECT userid FROM subs
        WHERE channelid="{}";""".format(channel_id))
    all_res = cur.fetchall()
    return all_res


# Возвращет все подпики пользователя по его user_id
def all_subs(user_id):
    cur.execute("""SELECT channelid FROM subs
        WHERE userid="{}";""".format(user_id))
    all_res = cur.fetchall()
    return all_res


def get_url(mes_id, user_id):
    cur.execute("""SELECT url FROM urls
            WHERE user_id="{}" and message_id={};""".format(user_id, mes_id))
    all_res = cur.fetchall()
    return all_res


def get_urls_all():
    cur.execute("""SELECT * FROM urls;""")
    all_res = cur.fetchall()
    return all_res


conn, cur = create_tables_if_not_exists()
