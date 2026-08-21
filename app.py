import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_connection, init_db, migrate_db, get_all_tags
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib import colors
from flask import make_response
import io


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
        
@app.route('/import', methods=['GET', 'POST'])
def import_notes():
    if request.method == 'POST':
        file = request.files.get('file')
        
        if not file or file.filename == '':
            flash('No file selected.', 'error')
            return redirect(url_for('import_notes'))
        
        filename = file.filename.lower()
        content = file.read().decode('utf-8')
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        imported = 0
        
        conn = get_connection()
        
        if filename.endswith('.txt'):
            title = file.filename.replace('.txt', '')
            word_count = len(content.split())
            conn.execute(
                'INSERT INTO notes (title, content, created_at, updated_at, word_count) VALUES (?, ?, ?, ?, ?)',
                (title, content, now, now, word_count)
            )
            imported = 1
            
        elif filename.endswith('.md'):
            lines = content.split('\n')
            title = "Imported Note"
            for line in lines:
                if line.startswith('# '):
                    title = line.replace('# ', '').strip()
                    break
            word_count = len(content.split())
            conn.execute(
                'INSERT INTO notes (title, content, created_at, updated_at, word_count) VALUES (?, ?, ?, ?, ?)',
                (title, content, now, now, word_count)
            )    
            imported = 1
            
        elif filename.endswith('.json'):
            import json as json_lib
            data = json_lib.loads(content)
            
            if isinstance(data, list):
                notes_data = data
            else:
                notes_data = [data]
                
            for item in notes_data:
                note_title = (item.get('title') or 
                              item.get('name') or
                              item.get('Name') or
                              'Imported Note')
                
                note_content = (item.get('textContent') or
                                item.get('content') or
                                item.get('Content') or
                                item.get('description') or '')
                
                if not note_content and 'listContent' in item:
                    note_content = '\n'.join([li.get('text', '') for li in item['listContent']])
                    
                if not note_content:
                    note_content = '\n'.join([f"{k}: {v}" for k, v in item.items()])
                    
                word_count = len(note_content.split())
                conn.execute(
                    'INSERT INTO notes (title, content, created_at, updated_at, word_count) VALUES (?, ?, ?, ?, ?)',
                    (note_title, note_content, now, now, word_count)
                )
                imported += 1
                
        elif filename.endswith('.csv'):
            import csv, io as csv_io
            reader = csv.DictReader(csv_io.StringIO(content))
            for row in reader:
                note_title = row.get('Name', row.get('Title', 'Imported Notion Note'))
                note_content = row.get('Content', row.get('Description', ''))
                word_count = len(note_content.split())
                conn.execute(
                    'INSERT INTO notes (title, content, created_at, updated_at, word_count) VALUES (?, ?, ?, ?, ?)',
                    (note_title, note_content, now, now, word_count)
                )
                imported += 1
                
        elif filename.endswith('.enex'):
            from xml.etree import ElementTree as ET
            root = ET.fromstring(content)
            for note_elem in root.findall('note'):
                note_title = note_elem.findtext('title') or 'Imported Note'
                note_content_raw = note_elem.findtext('content') or ''
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(note_content_raw, 'html.parser')
                note_content = soup.get_text(separator='\n').strip()
                word_count = len(note_content.split())
                conn.execute(
                    'INSERT INTO notes (title, content, created_at, updated_at, word_count) VALUES (?, ?, ?, ?, ?)',
                )
                imported += 1
            
        elif filename.endswith('.html'):
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            note_title = soup.title.string if soup.title else file.filename.replace('.html', '')
            note_content = soup.get_text(separator='\n').strip()
            word_count = len(note_content.split())
            conn.execute(
                'INSERT INTO notes (title, content, created_at, updated_at, word_count) VALUES (?, ?, ?, ?, ?)',
                (note_title, note_content, now, now, word_count)
            )
            imported += 1
            
        else:
            flash('Unsupported file format.', 'error')
            return redirect(url_for('import_notes'))
            
        conn.commit()
        conn.close()
        
        flash(f'Successfully imported {imported} notes(s).', 'success')
        return redirect(url_for('index'))
    return render_template('import.html')
    
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
    
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        updated_at = now
        word_count = len(content.split())
        
        
        if not title or not content:
            flash('Both title and content are required!', 'error')
            return render_template('edit.html', note=note)
        
        conn.close()
        
        conn = get_connection()
        conn.execute(
            'UPDATE notes SET title = ?, content = ?, updated_at = ?, word_count = ? WHERE id = ?',
            (title, content, updated_at, word_count, note_id)
        )
        
        raw_tags = request.form.get('tags', '')
        tag_list = [t.strip().lower() for t in raw_tags.split(',') if t.strip()]
        
        conn.execute('DELETE FROM note_tags WHERE note_id = ?', (note_id,))
        
        for tag_name in tag_list:
            conn.execute('INSERT OR IGNORE INTO tags (name) VALUES (?)', (tag_name,))
            tag = conn.execute('SELECT id FROM tags WHERE name = ?', (tag_name,)).fetchone()
            conn.execute('INSERT OR IGNORE INTO note_tags (note_id, tag_id) VALUES (?, ?)', (note_id, tag['id']))
            
        conn.commit()
        conn.close()
        
        flash('Note has been updated successfully!', 'success')
        return redirect(url_for('index'))
    
    existing_tags = conn.execute('''
        SELECT tags.name FROM tags
        JOIN note_tags ON tags.id = note_tags.tag_id
        WHERE note_tags.note_id = ?
    ''', (note_id,)).fetchall()
    
    tag_string = ', '.join([t['name'] for t in existing_tags])
    conn.close()
    return render_template('edit.html', note=note, tag_string=tag_string)

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

@app.route('/export/all')
def export_all_notes():
    conn = get_connection()
    notes = conn.execute('SELECT * FROM notes ORDER BY is_pinned DESC, created_at DESC').fetchall()
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=inch, leftMargin=inch,
                            topMargin=inch, bottomMargin=inch)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('title', fontSize=18, fontName='Times-Bold', spaceAfter=6)
    meta_style = ParagraphStyle('meta', fontSize=9, fontName='Times-Roman', textColor=colors.grey, spaceAfter=4)
    body_style = ParagraphStyle('body', fontSize=12, fontName='Times-Roman', leading=16, spaceAfter=16, wordWrap='LTR')
    header_style = ParagraphStyle('header', fontSize=26, fontName='Times-Bold', spaceAfter=16, textColor=colors.HexColor('#3b82f6'))
    
    story = [
        Paragraph('My Notes', header_style),
        HRFlowable(width="100%", thickness=2, color=colors.HexColor('#3b82f6')),
        Spacer(1, 20),
    ]
    
    for note in notes:
        tags = conn.execute('''
            SELECT tags.name FROM tags
            JOIN note_tags ON tags.id = note_tags.tag_id
            WHERE note_tags.note_id = ?
        ''', (note['id'],)).fetchall()
        
        tag_names = ', '.join([t['name'] for t in tags]) if tags else 'No tags'
        
        story.extend([
            Paragraph(note['title'], title_style),
            Spacer(1, 4),
            Paragraph(f"Created: {note['created_at']} · {note['word_count']} words · Tags: {tag_names}", meta_style),
            Spacer(1, 8),
            Paragraph(note['content'].replace('\n', '<br/>'), body_style),
            Spacer(1, 8),
            HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e5e7eb')),
            Spacer(1, 12),
        ])
        
    conn.close()
    doc.build(story)
    buffer.seek(0)
        
    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename="all_notes.pdf"'
    return response

@app.route('/export/<int:note_id>')
def export_note(note_id):
    conn = get_connection()
    note = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
    tags = conn.execute('''
        SELECT tags.name FROM tags
        JOIN note_tags ON tags.id = note_tags.tag_id
        WHERE note_tags.note_id = ?
    ''', (note_id,)).fetchall()
    conn.close()
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=inch, leftMargin=inch,
                            topMargin=inch, bottomMargin=inch)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('title', fontSize=24, fontName='Times-Bold', spaceAfter=12)
    meta_style = ParagraphStyle('meta', fontSize=10, fontName='Times-Roman', textColor=colors.grey, spaceAfter=6)
    body_style = ParagraphStyle('body', fontSize=12, fontName='Times-Roman', leading=20, spaceAfter=12)
    tag_style = ParagraphStyle('tag', fontSize=10, fontName='Times-Roman', textColor=colors.HexColor('#3b82f6'))
    
    tag_names = ', '.join([t['name'] for t in tags]) if tags else 'No tags'
    
    story = [
        Paragraph(note['title'], title_style),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')),
        Spacer(1, 12),
        Paragraph(f"Created: {note['created_at']} · Updated: {note['updated_at']} · {note['word_count']} words", meta_style),
        Paragraph(f"Tags: {tag_names}", tag_style),
        Spacer(1, 20),
        Paragraph(note['content'].replace('\n', '<br/>'), body_style),
    ]
    
    doc.build(story)
    buffer.seek(0)
    
    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="{note["title"]}.pdf"'
    return response

@app.route('/note/<int:note_id>')
def view_note(note_id):
    conn = get_connection()
    note = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
    tags = conn.execute('''
        SELECT tags.name FROM tags
        JOIN note_tags ON tags.id = note_tags.tag_id
        WHERE note_tags.note_id = ?
    ''', (note_id,)).fetchall()
    conn.close()
    tag_names = [t['name'] for t in tags]
    return render_template('view_note.html', note=note, tags=tag_names)

@app.template_filter('format_date')
def format_value(value):
    if not value:
        return ''
    
    try:
        from datetime import datetime
        dt = datetime.strptime(value, '%Y-%m-%d %H:%M:$S')
        return dt.strftime('%-d %b').lstrip('0')
    except:
        return value
    
    
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')