import sqlite3
import hashlib
import secrets
from contextlib import contextmanager
from pathlib import Path

DB = Path(__file__).with_name('tracker.db')
STATUSES = ('Offen', 'Beworben', 'Vorstellungsgespräch', 'Zusage', 'Absage')

@contextmanager
def connect():
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON')
        try:
            yield conn
        finally:
            pass
    conn.close()

def init_db():
    with connect() as conn:
        conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL,
            salt TEXT NOT NULL, password_hash TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id),
            company TEXT NOT NULL, position TEXT NOT NULL, applied_on TEXT NOT NULL,
            status TEXT NOT NULL, notes TEXT NOT NULL DEFAULT ''
        );
        ''')

def hash_password(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 600_000).hex()

def register(username, password):
    username = username.strip().lower()
    if not username or len(password) < 8:
        raise ValueError('Benutzername und mindestens 8 Zeichen Passwort erforderlich.')
    salt = secrets.token_hex(16)
    try:
        with connect() as conn:
            conn.execute('INSERT INTO users (username,salt,password_hash) VALUES (?,?,?)',
                         (username, salt, hash_password(password, salt)))
    except sqlite3.IntegrityError:
        return False
    return True

def login(username, password):
    with connect() as conn:
        user = conn.execute('SELECT * FROM users WHERE username=?', (username.strip().lower(),)).fetchone()
    if user and secrets.compare_digest(user['password_hash'], hash_password(password, user['salt'])):
        return user['id']
    return None

def validate(company, position, status):
    if not company.strip() or not position.strip() or status not in STATUSES:
        raise ValueError('Firma, Stelle und gültiger Status erforderlich.')

def add_application(user_id, company, position, applied_on, status, notes=''):
    validate(company, position, status)
    with connect() as conn:
        return conn.execute('INSERT INTO applications (user_id,company,position,applied_on,status,notes) VALUES (?,?,?,?,?,?)',
                            (user_id,company.strip(),position.strip(),str(applied_on),status,notes)).lastrowid

def list_applications(user_id):
    with connect() as conn:
        return [dict(row) for row in conn.execute('SELECT id,company,position,applied_on,status,notes FROM applications WHERE user_id=? ORDER BY applied_on DESC,id DESC', (user_id,))]

def update_application(user_id, app_id, company, position, applied_on, status, notes=''):
    validate(company, position, status)
    with connect() as conn:
        return conn.execute('UPDATE applications SET company=?,position=?,applied_on=?,status=?,notes=? WHERE id=? AND user_id=?',
                            (company.strip(),position.strip(),str(applied_on),status,notes,app_id,user_id)).rowcount

def delete_application(user_id, app_id):
    with connect() as conn:
        return conn.execute('DELETE FROM applications WHERE id=? AND user_id=?', (app_id,user_id)).rowcount
