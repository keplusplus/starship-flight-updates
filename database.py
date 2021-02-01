import sqlite3, telebot

conn = sqlite3.connect(r'.\starship-flight-updates\starship.db')
c = conn.cursor()

def setup_database():
    c.execute('DROP TABLE closure')
    c.execute("CREATE TABLE 'closure' ('id' INTEGER PRIMARY KEY AUTOINCREMENT,'begin' TIMESTAMP NOT NULL,'end' TIMESTAMP NOT NULL,'valid' BOOLEAN NOT NULL DEFAULT TRUE);")
    conn.commit()

def append_cameroncounty(data: list):
    for d in data:
        if c.execute('SELECT valid FROM closure WHERE begin = ? AND end = ?',(d['begin'],d['end'])).fetchone():   #in database
            if c.execute('SELECT valid FROM closure WHERE begin = ? AND end = ?',(d['begin'],d['end'])).fetchone()[0] != d['valid']:   #smth changed
                telebot.send_message(None,'Closure change!') #TODO
                c.execute('UPDATE closure SET valid = ? WHERE begin = ? AND end = ?',(d['valid'],d['begin'],d['end']))
        else:   #not in database
            c.execute('INSERT INTO closure(begin, end, valid) VALUES(?,?,?)',(d.values()))
            telebot.send_message(None,'New Closure!') #TODO
        for valid in c.execute('SELECT begin, end, valid FROM closure WHERE valid = TRUE').fetchall():
            if valid not in d:
                c.execute('UPDATE closure SET valid = FALSE WHERE begin = ? AND end = ? AND valid = ?', list(valid))
    conn.commit()
