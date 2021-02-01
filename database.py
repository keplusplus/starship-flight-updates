import sqlite3, telebot, datetime

conn = sqlite3.connect(r'.\starship-flight-updates\starship.db')
c = conn.cursor()

def setup_database():
    c.execute('DROP TABLE closure')
    c.execute("CREATE TABLE 'closure' ('id' INTEGER PRIMARY KEY AUTOINCREMENT,'begin' TIMESTAMP NOT NULL,'end' TIMESTAMP NOT NULL,'valid' BOOL);")
    conn.commit()

def append_cameroncounty(data: list):
    data_as_list = []
    for d in data:
        data_as_list.append(tuple(d.values()))
        if c.execute('SELECT valid FROM closure WHERE begin = ? AND end = ?',(d['begin'],d['end'])).fetchone():   #in database
            if c.execute('SELECT valid FROM closure WHERE begin = ? AND end = ?',(d['begin'],d['end'])).fetchone()[0] != d['valid']:   #smth changed
                print('Closure change')
                #telebot.send_message(None,'Closure change!') #TODO
                c.execute('UPDATE closure SET valid = ? WHERE begin = ? AND end = ?',(d['valid'],d['begin'],d['end']))
        else:   #not in database
            c.execute('INSERT INTO closure(begin, end, valid) VALUES(?,?,?)',list(list(d.values())))
            conn.commit()
            print('New Closure: ',list(d.values()))
            #telebot.send_message(None,'New Closure!') #TODO
    print(data_as_list)
    for valid in c.execute('SELECT begin, end, valid FROM closure WHERE valid = TRUE').fetchall():  #update old valid closures -> FALSE
        if (datetime.datetime.strptime(valid[0],'%Y-%m-%d %H:%M:%S'),datetime.datetime.strptime(valid[1],'%Y-%m-%d %H:%M:%S'),valid[2]) not in data_as_list:
            print('not in data')
            c.execute('UPDATE closure SET valid = FALSE WHERE begin = ? AND end = ? AND valid = ?', list(valid))
    conn.commit()