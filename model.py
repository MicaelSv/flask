import sqlite3


def create_db():
    conn = sqlite3.connect('atendimento.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS pacientes (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   nome TEXT NOT NULL,
                   idade INTEGER,
                   email TEXT,
                   cpf TEXT UNIQUE,
                   senha TEXT
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS medico (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   nome TEXT NOT NULL,
                   crm TEXT UNIQUE,
                   especialidade TEXT,
                   senha TEXT
    )''')

    conn.commit()
    conn.close()
