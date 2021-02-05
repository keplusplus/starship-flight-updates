import sqlite3, telebot, datetime

conn = sqlite3.connect(r'.\starship-flight-updates\starship.db')
c = conn.cursor()

def setup_database():
    c.execute('DROP TABLE closure')
    c.execute("CREATE TABLE 'closure' ('id' INTEGER PRIMARY KEY AUTOINCREMENT,'begin' TIMESTAMP NOT NULL,'end' TIMESTAMP NOT NULL,'valid' BOOL, 'announced' BOOL DEFAULT FALSE);")
    c.execute('DROP TABLE faa')
    c.execute("CREATE TABLE 'faa' ('id' INTEGER PRIMARY KEY AUTOINCREMENT,'begin' TIMESTAMP NOT NULL,'end' TIMESTAMP NOT NULL,'fromSurface' BOOL, toAltitude INTEGER, 'announced' BOOL DEFAULT FALSE);")
    conn.commit()

def to_utc_time(time: datetime.datetime) -> datetime.datetime:
    return time + datetime.timedelta(hours=6)

def datetime_to_string(dtime: datetime) -> str:
    if isinstance(dtime, datetime.time):
        return dtime.strftime('%H:%M')
    if dtime.date() == datetime.date.today():
        return dtime.strftime('%H:%M')
    return dtime.strftime('%b %d %H:%M')

def time_to_string_local(time: datetime.datetime) -> str:
    return (time-datetime.timedelta(hours=6)).strftime('%H:%M')

def sql_to_datetime(date: str) -> datetime.datetime:
    return datetime.datetime.strptime(date,'%Y-%m-%d %H:%M:%S')


def append_cameroncounty(data: list, message:bool = True, daily_time:datetime.datetime = datetime.time(10,0)):   #daily = daily update message -> does not want any changes as extra message
    data_as_list = []   #needed to check if data in db was removed from live
    for d in data:
        d['begin'], d['end'] = to_utc_time(d['begin']), to_utc_time(d['end'])
        data_as_list.append((d['begin'], d['end']))
        if c.execute('SELECT * FROM closure WHERE begin = ? OR end = ?',(d['begin'],d['end'])).fetchone():   #in database
            in_db = c.execute('SELECT begin,end,valid,announced FROM closure WHERE begin = ? OR end = ?',(d['begin'],d['end'])).fetchone()
            if message and in_db[3]:
                if in_db[2] != d['valid']:  #valid changed
                    if d['valid']:  #now valid
                        telebot.send_channel_message("Today's road closure has been rescheduled!✅\n(<i>From "+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+' UTC)</i>)')
                    else:   #now unvalid
                        telebot.send_channel_message("Today's road closure has been canceled!❌\n(<i><s>From "+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+'</s> UTC)</i>)')
                if in_db[0] != d['begin']:  #begin has changed
                    telebot.send_channel_message("Today's road closure has changed:✅\n<i>From "+datetime_to_string(sql_to_datetime(in_db[0]))+' to '+datetime_to_string(sql_to_datetime(in_db[1]))+'</i>(UTC)<i>\n➡️ From '+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+'</i>(UTC)')
                if in_db[1] != d['end']:    #end has changed
                    telebot.send_channel_message("Today's road closure has changed:✅\n<i>From "+datetime_to_string(sql_to_datetime(in_db[0]))+' to '+datetime_to_string(sql_to_datetime(in_db[1]))+'</i>(UTC)<i>\n➡️ From '+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+'</i>(UTC)')
            c.execute('UPDATE closure SET begin = ?, end = ?, valid = ? WHERE begin = ? OR end = ?',(d['begin'],d['end'],d['valid'],d['begin'],d['end']))
        else:   #not in db
            announced = False
            if datetime.datetime.now().time() > daily_time and (d['begin'].date() == datetime.date.today() or datetime.date.today() == d['end'].date()) and d['end'] > datetime.datetime.now():
                announced = True
                if message:
                    telebot.send_channel_message('A new road closuer has been scheduled!✅\n(<i>From '+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+'</i>(UTC)')
            c.execute('INSERT INTO closure(begin,end,valid,announced) VALUES(?,?,?,?)',(d['begin'],d['end'],d['valid'],announced))
    for in_db in c.execute('SELECT id, begin,end FROM closure WHERE valid = True').fetchall():
        if (in_db[1],in_db[2]) not in data_as_list:
            c.execute('DELETE FROM closure WHERE id = ?',(in_db[0],))
            if message and (sql_to_datetime(in_db[1]) <= datetime.datetime.now() <= sql_to_datetime(in_db[2])):
                telebot.send_channel_message('An active road closure has been canceled!❌\n(<i><s>From '+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+'</s> (UTC)</i>)')
    conn.commit()              

def announce_today_closures():
    c.execute('UPDATE closure SET announced = TRUE WHERE DATE(begin) = ? OR DATE(end) = ?',(datetime.date.today(),datetime.date.today()))
    conn.commit()

def road_closure_today():   #for daily update
    out = [False]
    for x in c.execute('SELECT begin, end, valid FROM closure WHERE DATE(begin) = ? OR DATE(end) = ?',(datetime.date.today(),datetime.date.today())).fetchall():
        if x[2]:
            out[0] = True
            out.append((sql_to_datetime(x[0]),sql_to_datetime(x[1]),x[2]))
    return out

def append_faa(data, message:bool = True, daily_time:datetime.datetime = datetime.time(10,0)):
    data_as_list = []   #needed to check if data in db was removed from live
    for d in data:
        d['begin'], d['end'] = to_utc_time(d['begin']), to_utc_time(d['end'])
        if d['toAltitude'] > 0:
            #d['toAltitude'] = round(d['toAltitude']*0.0003048,3) km
            pass
        data_as_list.append((d['begin'], d['end']))
        if c.execute('SELECT * FROM faa WHERE begin = ? AND end = ?',(d['begin'], d['end'])).fetchone():   #in db
            #changed faa
            in_db = c.execute('SELECT begin,end,fromSurface,toAltitude,announced FROM faa WHERE begin = ? AND end = ?',(d['begin'], d['end'])).fetchone()
            if message and in_db[4]:
                if in_db[2] != d['fromSurface'] and in_db[3] != d['toAltitude']:
                    telebot.send_channel_message('missing')
                elif in_db[2] != d['fromSurface']:
                    telebot.send_channel_message('missing')
                elif in_db[3] != d['toAltitude']:
                    if d['toAltitude'] == -1:
                        telebot.send_channel_message('TFR max altitude has changed✅\nMax alt. is now unlimited (was '+str(in_db[3])+'ft), flight is possible!\n<i>From '+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+' (UTC)</i>')
                    else:
                        was = str(in_db[3])
                        if in_db[3] == -1:
                            was = 'unlimited'
                        telebot.send_channel_message('TFR max altitude has changed❌\nMax alt. is now '+srt(d['toAltitude'])+'ft (was '+was+' ft), flight is not possible!\n<i>From '+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+' (UTC)</i>')
            c.execute('UPDATE faa SET fromSurface = ?, toAltitude = ? WHERE begin = ? AND end = ?',(d['fromSurface'],d['toAltitude'],d['begin'], d['end']))
        else:   #not in db
            #new faa
            announced = False
            if datetime.datetime.now().time() > daily_time and (d['begin'].date() == datetime.date.today() or datetime.date.today() == d['end'].date()) and d['end'] > datetime.datetime.now():
                announced = True
                if message:
                    if d['toAltitude'] == -1:
                        telebot.send_channel_message('New TFR has been issued✅\nMax alt.: unlimited, flight is possible!\n<i>From '+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+' (UTC)</i>')
                    else:
                        telebot.send_channel_message('New TFR has been issued❌\nMax alt.: '+str(d['toAltitude'])+' ft, flight is not possible!\n<i>From '+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+' (UTC)</i>')
            c.execute('INSERT INTO faa(begin,end,fromSurface,toAltitude,announced) VALUES(?,?,?,?,?)',(d['begin'],d['end'],d['fromSurface'],d['toAltitude'],announced))
    #deleted faa
    for in_db in c.execute('SELECT begin, end FROM faa').fetchall():
        if not (sql_to_datetime(in_db[0]),sql_to_datetime(in_db[1])) in data_as_list:
            if message and (sql_to_datetime(in_db[0]) <= datetime.datetime.now() <= sql_to_datetime(in_db[1])):
                telebot.send_channel_message('missing')
            c.execute('DELETE FROM faa WHERE begin = ? AND end = ?',(sql_to_datetime(in_db[0]),sql_to_datetime(in_db[1])))
    conn.commit()

def announce_today_faas():
    c.execute('UPDATE faa SET announced = TRUE WHERE DATE(begin) = ? OR DATE(end) = ?',(datetime.date.today(),datetime.date.today()))
    conn.commit()

def faa_today():
    out = [False]
    for in_db in c.execute('SELECT begin, end, toAltitude FROM faa').fetchall():
        if sql_to_datetime(in_db[0]).date() <= datetime.date.today() <= sql_to_datetime(in_db[1]).date():
            if in_db[2] == -1:
                out[0] = True
                out.append((sql_to_datetime(in_db[0]),sql_to_datetime(in_db[1]),in_db[2],True))
            else:
                out.append((sql_to_datetime(in_db[0]),sql_to_datetime(in_db[1]),in_db[2],False))
    return out