import sqlite3, telebot, datetime

conn = sqlite3.connect(r'.\starship-flight-updates\starship.db')
c = conn.cursor()

def setup_database():
    c.execute('DROP TABLE closure')
    c.execute("CREATE TABLE 'closure' ('id' INTEGER PRIMARY KEY AUTOINCREMENT,'begin' TIMESTAMP NOT NULL,'end' TIMESTAMP NOT NULL,'valid' BOOL);")
    conn.commit()

def sql_to_datetime(date: str) -> datetime.datetime:
    return datetime.datetime.strptime(date,'%Y-%m-%d %H:%M:%S')

def append_cameroncounty(data: list):
    data_as_list = []
    for d in data:
        data_as_list.append(tuple(d.values()))
        if c.execute('SELECT valid FROM closure WHERE DATE(begin) = ? AND DATE(end) = ?',(d['begin'].date(),d['end'].date())).fetchone():   #in database
            in_db = c.execute('SELECT begin, end, valid FROM closure WHERE DATE(begin) = ? AND DATE(end) = ?',(d['begin'].date(),d['end'].date())).fetchone()
            if (sql_to_datetime(in_db[0]), sql_to_datetime(in_db[1])) != (d['begin'], d['end']):   #time has changed
                print('Closure Time change')
                c.execute('UPDATE closure SET begin = ?, end = ? WHERE begin = ? AND end = ?',(d['begin'],d['end'],sql_to_datetime(in_db[0]), sql_to_datetime(in_db[1])))
            if in_db[2] != d['valid']:  #valid has changed
                print('Closure is now'+str(d['valid']))
                c.execute('UPDATE closure SET valid = ? WHERE begin = ? AND end = ?',(d['valid'],d['begin'],d['end']))
        else:   #not in database
            c.execute('INSERT INTO closure(begin, end, valid) VALUES(?,?,?)',list(list(d.values())))
            conn.commit()
            print('New Closure: ',list(d.values()))
    for valid in c.execute('SELECT begin, end, valid FROM closure WHERE valid = TRUE').fetchall():  #update old valid closures -> FALSE
        if (sql_to_datetime(valid[0]),sql_to_datetime(valid[1]),valid[2]) not in data_as_list:
            print('Closure gone from site')
            c.execute('UPDATE closure SET valid = FALSE WHERE begin = ? AND end = ? AND valid = ?', list(valid))
    conn.commit()