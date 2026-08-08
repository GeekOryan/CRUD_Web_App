import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_connection, init_db, migrate_db

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-123')

init_db()
migrate_db()

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        created_at = now
        updated_at = now
        word_count = len(content.split())
        
        if not title or not content:
            flash('Both title and content are required!', 'error')
            return render_template('create.html', title = title, content = content)
        
        conn = sqlite3.connect('notes.db')
        conn.execute(
            'INSERT INTO notes (title, content, created_at, updated_at, word_count) VALUES (?, ?, ?, ?, ?)',
            (title, content, created_at, updated_at, word_count)
        )
        
        conn.commit()
        conn.close()
        
        flash('Note create successfully!', 'success')
        return redirect(url_for('index'))
    
    else:
        return render_template('create.html')
        
    
@app.route('/')
def index():
    conn = get_connection()
    query = request.args.get('q' '')
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
    
    return render_template('edit.html', note=note)

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