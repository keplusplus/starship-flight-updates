import sqlite3, telebot, datetime

conn = sqlite3.connect(r'.\starship-flight-updates\starship.db')
c = conn.cursor()

def setup_database():
    c.execute('DROP TABLE closure')
    c.execute("CREATE TABLE 'closure' ('id' INTEGER PRIMARY KEY AUTOINCREMENT,'begin' TIMESTAMP NOT NULL,'end' TIMESTAMP NOT NULL,'valid' BOOL);")
    conn.commit()

def to_utc_time(time: datetime.datetime) -> datetime.datetime:
    return time + datetime.timedelta(hours=6)

def time_to_string(time: datetime.datetime) -> str:
    return time.strftime('%H:%M')

def time_to_string_local(time: datetime.datetime) -> str:
    return (time-datetime.timedelta(hours=6)).strftime('%H:%M')

def sql_to_datetime(date: str) -> datetime.datetime:
    return datetime.datetime.strptime(date,'%Y-%m-%d %H:%M:%S')

def append_cameroncounty(data: list, daily:bool = False):   #daily = daily update message -> does not want any changes as extra message
    data_as_list = []
    for d in data:
        d['begin'], d['end'] = to_utc_time(d['begin']), to_utc_time(d['end'])
        data_as_list.append(tuple(d.values()))
        if c.execute('SELECT valid FROM closure WHERE DATE(begin) = ? AND DATE(end) = ?',(d['begin'].date(),d['end'].date())).fetchone():   #in database
            in_db = c.execute('SELECT begin, end, valid FROM closure WHERE DATE(begin) = ? AND DATE(end) = ?',(d['begin'].date(),d['end'].date())).fetchone()
            d['valid'] = False
            if in_db[2] != d['valid']:  #valid has changed
                print('valid changed!')
                if not daily and sql_to_datetime(in_db[0]).date() == datetime.datetime.today().date():
                    if d['valid']:
                        telebot.send_channel_message("Today's road closure has been rescheduled\!\n\(From "+time_to_string(d['begin'])+' to '+time_to_string(d['end'])+' UTC\)')
                    else:
                        telebot.send_channel_message("Today's road closure has been canceled\!\n\(~From "+time_to_string(d['begin'])+' to '+time_to_string(d['end'])+'~ UTC\)')
                c.execute('UPDATE closure SET begin = ?, end = ?, valid = ? WHERE begin = ? AND end = ?',(d['begin'],d['end'],d['valid'],in_db[0],in_db[1]))
            elif (sql_to_datetime(in_db[0]), sql_to_datetime(in_db[1])) != (d['begin'], d['end']):   #time has changed
                if not daily and sql_to_datetime(in_db[0]).date() == datetime.datetime.today().date():
                    telebot.send_channel_message("Today's road closure has changed:\(UTC\)\n❌  "+time_to_string(sql_to_datetime(in_db[0]))+' to '+time_to_string(sql_to_datetime(in_db[1]))+'\n➡️  '+time_to_string(d['begin'])+' to '+time_to_string(d['end']))
                c.execute('UPDATE closure SET begin = ?, end = ? WHERE begin = ? AND end = ?',(d['begin'],d['end'],sql_to_datetime(in_db[0]), sql_to_datetime(in_db[1])))
        else:   #not in database
            c.execute('INSERT INTO closure(begin, end, valid) VALUES(?,?,?)',list(list(d.values())))
            conn.commit()
            print('New Closure: ',list(d.values()))
    for valid in c.execute('SELECT begin, end, valid FROM closure WHERE valid = TRUE').fetchall():  #update old valid closures -> FALSE
        if (sql_to_datetime(valid[0]),sql_to_datetime(valid[1]),valid[2]) not in data_as_list:
            print('Closure gone from site')
            c.execute('UPDATE closure SET valid = FALSE WHERE begin = ? AND end = ? AND valid = ?', list(valid))
    conn.commit()