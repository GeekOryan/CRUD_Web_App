import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_connection, init_db, migrate_db, get_all_tags

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-123')

init_db()
migrate_db()

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        raw_tags = request.form.get('tags', '')
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        tag_list = [t.strip().lower() for t in raw_tags.split(',') if t.strip()]
        
        created_at = now
        updated_at = now
        word_count = len(content.split())
        
        if not title or not content:
            flash('Both title and content are required!', 'error')
            return render_template('create.html', title = title, content = content)
        
        conn = get_connection()
        
        conn.execute(
            'INSERT INTO notes (title, content, created_at, updated_at, word_count) VALUES (?, ?, ?, ?, ?)',
            (title, content, created_at, updated_at, word_count)
        )
        
        new_note_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        
        for tag_name in tag_list:
            
            conn.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
            
            tag = conn.execute('SELECT id FROM tags WHERE name = ?', (tag_name,)).fetchone()
            
            conn.execute('INSERT OR IGNORE INTO note_tags (note_id, tag_id) VALUES (?, ?)', (new_note_id, tag['id']))
        
        conn.commit()
        conn.close()
        
        flash('Note create successfully!', 'success')
        return redirect(url_for('index'))
    
    else:
        tags = get_all_tags()
        return render_template('create.html', tags=tags)
        
    
@app.route('/')
def index():
    conn = get_connection()
    query = request.args.get('q', '')
    search_term = f"%{query}%"
    
    if query:
        notes = conn.execute(
            'SELECT * FROM notes WHERE title LIKE ? OR content LIKE ? ORDER BY is_pinned DESC, created_at DESC',
            (search_term, search_term)
        ).fetchall()
    else:
        notes = conn.execute(
            'SELECT * FROM notes ORDER BY is_pinned DESC, created_at DESC'
        ).fetchall()
        
    notes = [dict(note) for note in notes]
    for note in notes:
        tags = conn.execute('''
            SELECT tags.name FROM tags
            JOIN note_tags ON tags.id = note_tags.tag_id
            WHERE note_tags.note_id = ?
        ''', (note['id'],)).fetchall()
        note['tags'] = [tag['name'] for tag in tags]
        
    conn.close()
    return render_template('index.html', notes=notes, query=query or '')

@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit(note_id):
    conn = get_connection()
    note = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
    conn.close()
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        updated_at = now
        word_count = len(content.split())
        
        
        if not title or not content:
            flash('Both title and content are required!', 'error')
            return render_template('edit.html', note=note)
        
        conn = get_connection()
        conn.execute(
            'UPDATE notes SET title = ?, content = ?, updated_at = ?, word_count = ? WHERE id = ?',
            (title, content, updated_at, word_count, note_id)
        )
        conn.commit()
        conn.close()
        
        flash('Note has been updated successfully!', 'success')
        return redirect(url_for('index'))
    tags = get_all_tags()
    return render_template('edit.html', note=note, tags=tags)

@app.route('/delete/<int:note_id>')
def delete(note_id):
    conn = get_connection()
    conn.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    conn.commit()
    conn.close()
    flash('Note deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/pin/<int:note_id>')
def pin(note_id):
    conn = get_connection()
    conn.execute('UPDATE notes SET is_pinned = 1 - is_pinned WHERE id = ?', (note_id,))
    conn.commit()
    conn.close()
    flash('Note pinned successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)