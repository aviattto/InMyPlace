import sqlite3 as sq


async def sql_start():
    global db, cur
    db = sq.connect('inmyplace.db')
    cur = db.cursor()
    if db:
        print('Connected!')
    cur.execute("CREATE TABLE IF NOT EXISTS profile(user_id TEXT PRIMARY KEY)")
    db.commit()


async def create_profile(user_id):
    user = cur.execute("SELECT 1 FROM profile WHERE user_id == '{key}'".format(key=user_id)).fetchone()
    if not user:
        cur.execute("INSERT INTO profile VALUES(?)", (user_id,))
    db.commit()


def sql_read():
    cur.execute("SELECT 1 FROM profile")
    count = len(cur.fetchall())
    db.commit()
    return count
