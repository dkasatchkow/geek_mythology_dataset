import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, g

app = Flask(__name__)
DATABASE = 'relationships.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        object1 = request.form['object1']
        object2 = request.form['object2']
        relationship = request.form['relationship']

        db = get_db()
        db.execute('INSERT INTO relationships (object1, object2, relationship) VALUES (?, ?, ?)',
                   (object1, object2, relationship))
        db.commit()
        return redirect(url_for('index'))

    db = get_db()
    cursor = db.execute('SELECT * FROM relationships')
    relationships = cursor.fetchall()
    return render_template('index.html', relationships=relationships)

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True, port=5000)
