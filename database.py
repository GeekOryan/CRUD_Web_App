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
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS note_tags (
            note_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            FOREIGN KEY (note_id) REFERENCES notes(id),
            FOREIGN KEY (tag_id) REFERENCES tags(id),
            PRIMARY KEY (note_id, tag_id)
        )
    ''')
    conn.commit()
    conn.close()
    
def migrate_db():
    conn = get_connection()
    
    migrations = [
        "ALTER TABLE notes ADD COLUMN is_pinned INTEGER DEFAULT 0",
        "ALTER TABLE notes ADD COLUMN created_at TEXT",
        "ALTER TABLE notes ADD COLUMN updated_at TEXT",
        "ALTER TABLE notes ADD COLUMN word_count INTEGER DEFAULT 0",
        "CREATE TABLE IF NOT EXISTS tags (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE)",
        "CREATE TABLE IF NOT EXISTS note_tags (note_id INTEGER NOT NULL, tag_id INTEGER NOT NULL, FOREIGN KEY (note_id) REFERENCES notes(id), FOREIGN KEY (tag_id) REFERENCES tags(id), PRIMARY KEY (note_id, tag_id))"
    ]
    
    for migration in migrations:
        try:
            conn.execute(migration)
        except Exception:
            pass
        
    conn.commit()
    conn.close()
    
def get_all_tags():
    conn = get_connection()
    tags = conn.execute('SELECT * FROM tags ORDER BY name').fetchall()
    conn.close()
    return tags