# Notes — A Full-Stack Web Notes Application

## Live Demo
🔗 [https://crud-web-app-88jo.onrender.com](https://crud-web-app-88jo.onrender.com)

## About
A full-stack notes web application built for developers, students and anyone
who wants a fast, distraction-free place to capture and organise their
thoughts — without relying on a third-party app or surrendering their data
to someone else's server. Built entirely from scratch with Flask and SQLite,
deployed on Render.

## Features

**Core**
- Create, read, update and delete notes
- Collapsible grid card layout — collapsed view shows title, date, tags
  and word count. Click the card to read the full note. Click the chevron
  to reveal action buttons.
- Pin important notes to the top of the grid
- Real-time search by title and content

**Organisation**
- Tags — assign multiple tags per note, comma separated, displayed as pills
- Timestamps — created at and last updated at, stored automatically
- Word count — calculated and saved on every create and edit

**Export**
- Download any single note as a formatted PDF
- Download all notes as a multi-page PDF

**Import**
- Drag and drop file import supporting six formats:
  Markdown (.md), Plain Text (.txt), Google Keep (.json),
  Notion (.csv), Samsung Notes (.enex), OneNote (.html)

**UI/UX**
- Dark and light mode toggle with localStorage persistence
- Fluid gradient mesh background animated with GSAP
- Card shimmer and pulse glow animations — the page is alive without
  any user interaction required
- Fully responsive — works on desktop and mobile
- SVG icons throughout, no emojis in the interface
- Animated underline on navbar links

## Tech Stack
- **Backend** — Python, Flask, SQLite
- **Frontend** — HTML, CSS (custom variables), Tailwind CDN, JavaScript
- **Animations** — GSAP 3
- **PDF Generation** — ReportLab
- **NLP/Parsing** — BeautifulSoup4 (for HTML and ENEX import)
- **Deployment** — Render

## Run Locally

**Requirements:** Python 3.12+

```bash
git clone https://github.com/GeekOryan/CRUD_Web_App.git
cd CRUD_Web_App
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

## Screenshots
![Notes App](screenshot1.png)
![Dark Mode](screenshot2.png)
![New Note](screenshot3.png)