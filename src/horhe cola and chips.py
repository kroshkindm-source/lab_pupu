import sqlite3

conn = sqlite3.connect('kitov_A.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS zaselenie(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
flat INTEGER,
passport_num TEXT,
inst TEXT,
contacts TEXT,
obshaga_num INTEGER,
narush TEXT)''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS viselenie(
id INTEGER PRIMARY KEY AUTOINCREMENT,
id_vis INTEGER FOREIGNKEY REFERENCES zaselenie(id),
sost TEXT,
ready BOOLEAN)''')
conn.commit()
conn.close()

