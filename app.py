import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_connection, init_db

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-123')

init_db()

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        if not title or not content:
            flash('Both title and content are required!', 'error')
            return render_template('create.html', title = title, content = content)
        
        conn = sqlite3.connect('notes.db')
        conn.execute(
            'INSERT INTO notes (title, content) VALUES (?, ?)',
            (title, content)
        )
        conn.commit()
        conn.close()
        
        flash('Note create successfully!', 'success')
        return redirect(url_for('create'))
    
    else:
        return render_template('create.html')
        
    
    
def index():
    conn = get_connection()
    notes = conn.execute('SELECT * FROM notes').fetchall()
    conn.close()
    return render_template('index.html', notes = notes)


if __name__ == '__main__':
    app.run(debug=True)