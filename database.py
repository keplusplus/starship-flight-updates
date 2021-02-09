import sqlite3, telebot, datetime
from status import Status

db = r'.\starship-flight-updates\starship.db'

def reset_database():
    print('resetting db')
    conn = sqlite3.connect(db, timeout=20)
    c = conn.cursor()
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

def road_closure_today(conn = None):   #for daily update
    if conn is None:
        conn = sqlite3.connect(db, timeout=20)
    c = conn.cursor()
    out = [False]
    for x in c.execute('SELECT begin, end, valid FROM closure WHERE DATE(begin) <= ? AND end >= ?',(datetime.date.today(),datetime.datetime.utcnow())).fetchall():
        if x[2]:
            out[0] = True
            out.append((sql_to_datetime(x[0]),sql_to_datetime(x[1]),x[2]))
    c.execute('UPDATE closure SET announced = True WHERE DATE(begin) <= ? AND end >= ?',(datetime.date.today(),datetime.datetime.utcnow()))
    conn.commit()
    return out

def faa_today(conn = None):
    if conn is None:
        conn = sqlite3.connect(db, timeout=20)
    c = conn.cursor()
    out = [False]
    for in_db in c.execute('SELECT begin, end, toAltitude FROM faa WHERE DATE(begin) <= ? AND end >= ?',(datetime.date.today(),datetime.datetime.utcnow())).fetchall():
        if in_db[2] == -1:
            out[0] = True
            out.append((sql_to_datetime(in_db[0]),sql_to_datetime(in_db[1]),in_db[2],True))
        else:
            out.append((sql_to_datetime(in_db[0]),sql_to_datetime(in_db[1]),in_db[2],False))
    c.execute('UPDATE faa SET announced = TRUE WHERE DATE(begin) <= ? AND end >= ?',(datetime.date.today(),datetime.datetime.utcnow()))
    conn.commit()
    return out

def road_closure_active():  #used by thread
    conn = sqlite3.connect(db, timeout=20)  #needs own db because it's threaded
    c = conn.cursor()
    if c.execute('SELECT * from closure WHERE begin <= Datetime("now") AND end > Datetime("now") AND valid = True').fetchone():
        in_db = c.execute('SELECT begin, end from closure WHERE begin <= Datetime("now") AND end > Datetime("now") AND valid = True').fetchall()
        out = []
        for x in in_db:
            out.append((sql_to_datetime(x[0]),sql_to_datetime(x[1])))
        return out
    return []

def faa_active():  #in last min
    conn = sqlite3.connect(db, timeout=20)  #needs own db because it's threaded
    c = conn.cursor()
    if c.execute('SELECT * from faa WHERE begin <= Datetime("now") AND end > Datetime("now") AND toAltitude = -1').fetchone():
        in_db = c.execute('SELECT begin, end from faa WHERE begin <= Datetime("now") AND end > Datetime("now") AND toAltitude = -1').fetchall()
        out = []
        for x in in_db:
            out.append((sql_to_datetime(x[0]),sql_to_datetime(x[1])))
        return out
    return []

def append_cameroncounty(data: list, message:bool = True, daily_time:datetime.datetime = datetime.time(10,0)):   #daily = daily update message -> does not want any changes as extra message
    conn = sqlite3.connect(db, timeout=20)
    c = conn.cursor()
    #try:
    data_as_list = []   #needed to check if data in db was removed from live
    for d in data:
        d['begin'], d['end'] = to_utc_time(d['begin']), to_utc_time(d['end'])
        data_as_list.append((d['begin'], d['end']))
        if c.execute('SELECT * FROM closure WHERE begin = ? OR end = ?',(d['begin'],d['end'])).fetchone():   #in database
            in_db = c.execute('SELECT begin,end,valid,announced FROM closure WHERE begin = ? OR end = ?',(d['begin'],d['end'])).fetchone()
            if message and in_db[3]:
                if in_db[2] != d['valid']:  #valid changed
                    if d['valid']:  #now valid
                        telebot.send_channel_message("<b>Today's road closure has been rescheduled❕</b>\n(<i>From "+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+' UTC)</i>)'+Status().value_change_status(conn))
                    else:   #now unvalid
                        telebot.send_channel_message("<b>Today's road closure has been canceled!❗</b>\n(<i><s>From "+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+'</s> UTC)</i>)'+Status().value_change_status(conn))
                if sql_to_datetime(in_db[0]) != d['begin'] or sql_to_datetime(in_db[1]) != d['end']:  #begin has changed
                    telebot.send_channel_message("<b>Today's road closure has changed❕</b>\n<i>From "+datetime_to_string(sql_to_datetime(in_db[0]))+' to '+datetime_to_string(sql_to_datetime(in_db[1]))+'</i>(UTC)<i>\n➡️ From '+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+'</i>(UTC)'+Status().value_change_status(conn))
            c.execute('UPDATE closure SET begin = ?, end = ?, valid = ? WHERE begin = ? OR end = ?',(d['begin'],d['end'],d['valid'],d['begin'],d['end']))
        else:   #not in db
            print(d)
            announced = False
            if datetime.datetime.utcnow().time() > daily_time and d['begin'].date() <= datetime.date.today() and d['end'] > datetime.datetime.utcnow():   #TODO needs to be changed to avoid doublöe message
                announced = True
                if message:
                    telebot.send_channel_message('<b>A new road closure has been scheduled❕</b>\n(<i>From '+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+'</i> UTC)'+Status().value_change_status(conn))
            c.execute('INSERT INTO closure(begin,end,valid,announced) VALUES(?,?,?,?)',(d['begin'],d['end'],d['valid'],announced))
            print('in db')
    if data != []:
        for in_db in c.execute('SELECT id, begin,end FROM closure WHERE valid = True').fetchall():
            if (sql_to_datetime(in_db[1]),sql_to_datetime(in_db[2])) not in data_as_list:
                if message and (sql_to_datetime(in_db[1]) <= datetime.datetime.utcnow() <= sql_to_datetime(in_db[2])):
                    telebot.send_channel_message('<b>An active road closure has been canceled❗</b>\n(<i><s>From '+datetime_to_string(sql_to_datetime(in_db[1]))+' to '+datetime_to_string(sql_to_datetime(in_db[2]))+'</s> (UTC)</i>)'+Status().value_change_status(conn))
                print('deleting', in_db)
                c.execute('DELETE FROM closure WHERE id = ?',(in_db[0],))
    conn.commit()
    #except Exception as e:
    #    telebot.send_err_message('Error database-append-closure!\n\nException:\n' + str(e)) 

def announce_today_closures():
    conn = sqlite3.connect(db, timeout=20)
    c = conn.cursor()
    c.execute('UPDATE closure SET announced = TRUE WHERE DATE(begin) = ? OR DATE(end) = ?',(datetime.date.today(),datetime.date.today()))
    conn.commit()

def append_faa(data, message:bool = True, daily_time:datetime.datetime = datetime.time(10,0)):
    conn = sqlite3.connect(db, timeout=20)
    c = conn.cursor()
    try:
        data_as_list = []   #needed to check if data in db was removed from live
        for d in data:
            d['begin'], d['end'] = to_utc_time(d['begin']), to_utc_time(d['end'])
            data_as_list.append((d['begin'], d['end']))
            if c.execute('SELECT * FROM faa WHERE begin = ? AND end = ?',(d['begin'], d['end'])).fetchone():   #in db
                #changed faa
                in_db = c.execute('SELECT begin,end,fromSurface,toAltitude,announced FROM faa WHERE begin = ? AND end = ?',(d['begin'], d['end'])).fetchone()
                if message and in_db[4]:
                    if in_db[2] != d['fromSurface'] and in_db[3] != d['toAltitude']:
                        telebot.send_channel_message('<b>FromSurface and max. alt have changed to:</b>\n'+str(d['fromSurface'])+' and '+str(d['toAltitude'])+' ft'+Status().value_change_status(conn))
                    elif in_db[2] != d['fromSurface']:
                        telebot.send_channel_message('<b>FromSurface has changed to: '+str(d['fromSurface'])+'</b>'+Status().value_change_status(conn))
                    elif in_db[3] != d['toAltitude']:
                        if d['toAltitude'] == -1:
                            telebot.send_channel_message('<b>TFR max altitude has changed❕</b>\nMax alt. is now unlimited (was '+str(in_db[3])+'ft), flight is possible!\n<i>From '+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+' (UTC)</i>'+Status().value_change_status(conn))
                        else:
                            was = str(in_db[3])
                            if in_db[3] == -1:
                                was = 'unlimited'
                            telebot.send_channel_message('<b>TFR max altitude has changed❗</b>\nMax alt. is now '+str(d['toAltitude'])+'ft (was '+was+' ft), flight is not possible!\n<i>From '+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+' (UTC)</i>'+Status().value_change_status(conn))
                c.execute('UPDATE faa SET fromSurface = ?, toAltitude = ? WHERE begin = ? AND end = ?',(d['fromSurface'],d['toAltitude'],d['begin'], d['end']))
            else:   #not in db
                #new faa
                announced = False
                if datetime.datetime.now().time() > daily_time and d['begin'].date() <= datetime.date.today() and d['end'] > datetime.datetime.now():
                    announced = True
                    if message:
                        if d['toAltitude'] == -1:
                            telebot.send_channel_message('<b>New TFR has been issued❕</b>\nMax alt.: unlimited, flight is possible!\n<i>From '+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+' (UTC)</i>'+Status().value_change_status(conn))
                        else:
                            telebot.send_channel_message('<b>New TFR has been issued❗</b>\nMax alt.: '+str(d['toAltitude'])+' ft, flight is not possible!\n<i>From '+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+' (UTC)</i>'+Status().value_change_status(conn))
                c.execute('INSERT INTO faa(begin,end,fromSurface,toAltitude,announced) VALUES(?,?,?,?,?)',(d['begin'],d['end'],d['fromSurface'],d['toAltitude'],announced))
        #deleted faa
        if data != []:
            for in_db in c.execute('SELECT begin, end FROM faa').fetchall():
                if not (sql_to_datetime(in_db[0]),sql_to_datetime(in_db[1])) in data_as_list:
                    if message and (sql_to_datetime(in_db[0]) <= datetime.datetime.now() <= sql_to_datetime(in_db[1])): #TODO needs to be changed to avoid doublöe message
                        telebot.send_channel_message('<b>An active TFR has been removed❗</b>\n(<i><s>From '+datetime_to_string(in_db[0])+' to '+datetime_to_string(in_db[1])+'</s> (UTC)</i>)'+Status().value_change_status(conn))
                    c.execute('DELETE FROM faa WHERE begin = ? AND end = ?',(sql_to_datetime(in_db[0]),sql_to_datetime(in_db[1])))
        conn.commit()
    except Exception as e:
        telebot.send_err_message('Error database-append-faa!\n\nException:\n' + str(e))

def announce_today_faas():
    conn = sqlite3.connect(db, timeout=20)
    c = conn.cursor()
    c.execute('UPDATE faa SET announced = TRUE WHERE DATE(begin) = ? OR DATE(end) = ?',(datetime.date.today(),datetime.date.today()))
    conn.commit()
