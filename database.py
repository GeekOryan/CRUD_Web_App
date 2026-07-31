import sqlite3

def get_connection():
    conn = sqlite3.connect('notes.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    
def migrate_db():
    conn = get_connection()
    conn.execute('''
                ALTER TABLE notes
                ADD is_pinned INT DEFAULT 0;
                ADD created_at TEXT;
                ADD updated_at TEXT;
                ADD word_count INT DEFAULT 0;
                ''')