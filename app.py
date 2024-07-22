from flask import Flask, render_template, request, redirect, url_for
import string
import random
import sqlite3

app = Flask(__name__)

def get_db():
    db = sqlite3.connect('urls.db')
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('CREATE TABLE IF NOT EXISTS urls (id INTEGER PRIMARY KEY, original TEXT, short TEXT)')
        db.commit()

init_db()

def generate_short_url():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        original_url = request.form['url']
        if not original_url.startswith(('http://', 'https://')):
            original_url = 'http://' + original_url
        
        short_url = generate_short_url()
        
        db = get_db()
        db.execute('INSERT INTO urls (original, short) VALUES (?, ?)', (original_url, short_url))
        db.commit()
        
        full_short_url = url_for('redirect_to_url', short_url=short_url, _external=True)
        return render_template('home.html', short_url=full_short_url)
    return render_template('home.html')

@app.route('/<short_url>')
def redirect_to_url(short_url):
    db = get_db()
    result = db.execute('SELECT original FROM urls WHERE short = ?', (short_url,)).fetchone()
    if result:
        return redirect(result['original'])
    else:
        return "URL not found", 404

if __name__ == '__main__':
    app.run(debug=True)