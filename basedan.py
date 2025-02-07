import sqlite3

DB_FILE = "petitions.db"

# Ініціалізація бази даних
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS petitions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        votes_collected INTEGER,
                        days_remaining INTEGER,
                        url TEXT UNIQUE)''')
    conn.commit()
    conn.close()

# Збереження петиції в БД
def save_petition(petition):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''INSERT OR IGNORE INTO petitions (title, votes_collected, days_remaining, url)
                      VALUES (?, ?, ?, ?)''',
                   (petition['title'], petition['votes_collected'], petition['days_remaining'], petition['url']))
    conn.commit()
    conn.close()

# Отримання всіх петицій з БД
def get_petitions():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT title, votes_collected, days_remaining, url FROM petitions")
    petitions = cursor.fetchall()
    conn.close()
    return [{"title": row[0], "votes_collected": row[1], "days_remaining": row[2], "url": row[3]} for row in petitions]
