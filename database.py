import sqlite3, telebot, datetime
from data_sources import weather

conn = sqlite3.connect(r'.\starship-flight-updates\starship.db')
c = conn.cursor()

def reset_database():
    c.execute('DROP TABLE closure')
    c.execute("CREATE TABLE 'closure' ('id' INTEGER PRIMARY KEY AUTOINCREMENT,'begin' TIMESTAMP NOT NULL,'end' TIMESTAMP NOT NULL,'valid' BOOL, 'announced' BOOL DEFAULT FALSE);")
    c.execute('DROP TABLE faa')
    c.execute("CREATE TABLE 'faa' ('id' INTEGER PRIMARY KEY AUTOINCREMENT,'begin' TIMESTAMP NOT NULL,'end' TIMESTAMP NOT NULL,'fromSurface' BOOL, toAltitude INTEGER, 'announced' BOOL DEFAULT FALSE);")
    c.execute('DROP TABLE weather')
    c.execute("CREATE TABLE 'weather' ('id' INTEGER PRIMARY KEY AUTOINCREMENT,'weatherid' INTEGER NOT NULL,'windspeed' FLOAT NOT NULL,'timestamp' TIMESTAMP);")
    c.execute('DROP TABLE status')
    c.execute("CREATE TABLE 'status' ('id' INTEGER PRIMARY KEY AUTOINCREMENT,'flight' BOOL NOT NULL,'static' BOOL NOT NULL,'timestamp' TIMESTAMP);")
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

def road_closure_today():   #for daily update
    out = [False]
    for x in c.execute('SELECT begin, end, valid FROM closure WHERE DATE(begin) = ? OR DATE(end) = ?',(datetime.date.today(),datetime.date.today())).fetchall():
        if x[2]:
            out[0] = True
            out.append((sql_to_datetime(x[0]),sql_to_datetime(x[1]),x[2]))
    return out

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

def status() -> str:    #flight or static fire
    out = ''
    try:
        if c.execute('SELECT * FROM weather ORDER by id DESC LIMIT 1').fetchone():
            weather_in_db = c.execute('SELECT weatherid,windspeed FROM weather ORDER by id DESC LIMIT 1').fetchone()
            flight = (weather.weather(weather_in_db[0]) and weather.wind(weather_in_db[1]) and road_closure_today()[0] and faa_today()[0])
            static = road_closure_today()[0]
            if c.execute('SELECT * FROM status ORDER by id DESC LIMIT 1').fetchone():
                status_in_db = c.execute('SELECT flight,Static FROM status ORDER by id DESC LIMIT 1').fetchone()
                if status_in_db[0] != flight:
                    if flight:
                        out = '\n<u><b>Flight is now possible</b></u>🚀✅\n'
                    else:
                        out = '\n<u><b>Flight is no longer possible</b></u>🚀❌\n'
                if status_in_db[0] != static:
                    if static:
                        out+= '<i>Static fire or wdr are still possible</i>'
                    else:
                        return '<i>Nothing is possible anymore</i>'
                if status_in_db[0] == flight and status_in_db[0] == static:
                    return '\n[flight: '+str(flight)+'|staticfire: '+str(static)+']'
            c.execute('INSERT INTO status(flight,static,timestamp) VALUES(?,?,?)',(flight,static,datetime.datetime.now()))
            conn.commit()
    except Exception as e:
        telebot.send_err_message('Error database-status!\n\nException:\n' + str(e))
    return out

def append_cameroncounty(data: list, message:bool = True, daily_time:datetime.datetime = datetime.time(10,0)):   #daily = daily update message -> does not want any changes as extra message
    try:
        data_as_list = []   #needed to check if data in db was removed from live
        for d in data:
            d['begin'], d['end'] = to_utc_time(d['begin']), to_utc_time(d['end'])
            data_as_list.append((d['begin'], d['end']))
            if c.execute('SELECT * FROM closure WHERE begin = ? OR end = ?',(d['begin'],d['end'])).fetchone():   #in database
                in_db = c.execute('SELECT begin,end,valid,announced FROM closure WHERE begin = ? OR end = ?',(d['begin'],d['end'])).fetchone()
                if message and in_db[3]:
                    if in_db[2] != d['valid']:  #valid changed
                        if d['valid']:  #now valid
                            telebot.send_channel_message("<b>Today's road closure has been rescheduled!✅</b>\n(<i>From "+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+' UTC)</i>)'+status())
                        else:   #now unvalid
                            telebot.send_channel_message("<b>Today's road closure has been canceled!❌</b>\n(<i><s>From "+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+'</s> UTC)</i>)'+status())
                    if in_db[0] != d['begin']:  #begin has changed
                        telebot.send_channel_message("<b>Today's road closure has changed:✅</b>\n<i>From "+datetime_to_string(sql_to_datetime(in_db[0]))+' to '+datetime_to_string(sql_to_datetime(in_db[1]))+'</i>(UTC)<i>\n➡️ From '+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+'</i>(UTC)'+status())
                    if in_db[1] != d['end']:    #end has changed
                        telebot.send_channel_message("<b>Today's road closure has changed:✅</b>\n<i>From "+datetime_to_string(sql_to_datetime(in_db[0]))+' to '+datetime_to_string(sql_to_datetime(in_db[1]))+'</i>(UTC)<i>\n➡️ From '+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+'</i>(UTC)'+status())
                c.execute('UPDATE closure SET begin = ?, end = ?, valid = ? WHERE begin = ? OR end = ?',(d['begin'],d['end'],d['valid'],d['begin'],d['end']))
            else:   #not in db
                announced = False
                if datetime.datetime.now().time() > daily_time and d['begin'].date() <= datetime.date.today() and d['end'] > datetime.datetime.now():
                    announced = True
                    if message:
                        telebot.send_channel_message('<b>A new road closuer has been scheduled!✅</b>\n(<i>From '+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+'</i>(UTC)'+status())
                c.execute('INSERT INTO closure(begin,end,valid,announced) VALUES(?,?,?,?)',(d['begin'],d['end'],d['valid'],announced))
        if data != []:
            for in_db in c.execute('SELECT id, begin,end FROM closure WHERE valid = True').fetchall():
                if (in_db[1],in_db[2]) not in data_as_list:
                    if message and (sql_to_datetime(in_db[1]) <= datetime.datetime.now() <= sql_to_datetime(in_db[2])):
                        telebot.send_channel_message('<b>An active road closure has been canceled!❌</b>\n(<i><s>From '+datetime_to_string(in_db[1])+' to '+datetime_to_string(in_db[2])+'</s> (UTC)</i>)'+status())
                    c.execute('DELETE FROM closure WHERE id = ?',(in_db[0],))
        conn.commit()
    except Exception as e:
        telebot.send_err_message('Error database-append-closure!\n\nException:\n' + str(e)) 

def announce_today_closures():
    c.execute('UPDATE closure SET announced = TRUE WHERE DATE(begin) = ? OR DATE(end) = ?',(datetime.date.today(),datetime.date.today()))
    conn.commit()

def append_faa(data, message:bool = True, daily_time:datetime.datetime = datetime.time(10,0)):
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
                        telebot.send_channel_message('<b>FromSurface and max. alt have changed to:</b>\n'+str(d['fromSurface'])+' and '+str(d['toAltitude'])+' ft'+status())
                    elif in_db[2] != d['fromSurface']:
                        telebot.send_channel_message('<b>FromSurface has changed to: '+str(d['fromSurface'])+'</b>'+status())
                    elif in_db[3] != d['toAltitude']:
                        if d['toAltitude'] == -1:
                            telebot.send_channel_message('<b>TFR max altitude has changed✅</b>\nMax alt. is now unlimited (was '+str(in_db[3])+'ft), flight is possible!\n<i>From '+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+' (UTC)</i>'+status())
                        else:
                            was = str(in_db[3])
                            if in_db[3] == -1:
                                was = 'unlimited'
                            telebot.send_channel_message('<b>TFR max altitude has changed❌</b>\nMax alt. is now '+srt(d['toAltitude'])+'ft (was '+was+' ft), flight is not possible!\n<i>From '+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+' (UTC)</i>'+status())
                c.execute('UPDATE faa SET fromSurface = ?, toAltitude = ? WHERE begin = ? AND end = ?',(d['fromSurface'],d['toAltitude'],d['begin'], d['end']))
            else:   #not in db
                #new faa
                announced = False
                if datetime.datetime.now().time() > daily_time and d['begin'].date() <= datetime.date.today() and d['end'] > datetime.datetime.now():
                    announced = True
                    if message:
                        if d['toAltitude'] == -1:
                            telebot.send_channel_message('<b>New TFR has been issued✅</b>\nMax alt.: unlimited, flight is possible!\n<i>From '+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+' (UTC)</i>'+status())
                        else:
                            telebot.send_channel_message('<b>New TFR has been issued❌</b>\nMax alt.: '+str(d['toAltitude'])+' ft, flight is not possible!\n<i>From '+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+' (UTC)</i>'+status())
                c.execute('INSERT INTO faa(begin,end,fromSurface,toAltitude,announced) VALUES(?,?,?,?,?)',(d['begin'],d['end'],d['fromSurface'],d['toAltitude'],announced))
        #deleted faa
        if data != []:
            for in_db in c.execute('SELECT begin, end FROM faa').fetchall():
                if not (sql_to_datetime(in_db[0]),sql_to_datetime(in_db[1])) in data_as_list:
                    if message and (sql_to_datetime(in_db[0]) <= datetime.datetime.now() <= sql_to_datetime(in_db[1])):
                        telebot.send_channel_message('<b>An active TFR has been removed❌</b>\n(<i><s>From '+datetime_to_string(in_db[0])+' to '+datetime_to_string(in_db[1])+'</s> (UTC)</i>)'+status())
                    c.execute('DELETE FROM faa WHERE begin = ? AND end = ?',(sql_to_datetime(in_db[0]),sql_to_datetime(in_db[1])))
        conn.commit()
    except Exception as e:
        telebot.send_err_message('Error database-append-faa!\n\nException:\n' + str(e))

def announce_today_faas():
    c.execute('UPDATE faa SET announced = TRUE WHERE DATE(begin) = ? OR DATE(end) = ?',(datetime.date.today(),datetime.date.today()))
    conn.commit()

def append_weather(w):
    c.execute('INSERT INTO weather(weatherid,windspeed, timestamp) VALUES(?,?,?)',(w['weather'][0]['id'],w['wind_speed'],datetime.datetime.now()))
    conn.commit()

def weather_change(w):
    try:
        if c.execute('SELECT * FROM weather ORDER by id DESC LIMIT 1').fetchone():
            in_db = c.execute('SELECT weatherid,windspeed FROM weather ORDER by id DESC LIMIT 1').fetchone()
            if weather.weather_text(w)[1] != weather.weather(in_db[0]):
                if weather.weather_text(w)[1]:
                    telebot.send_channel_message('<b>Weather has changed:</b>✅\n<i>'+weather.weather_text(w)[0]+'</i>'+status())
                else:
                    telebot.send_channel_message('<b>Weather has changed:</b>❌\n<i>'+weather.weather_text(w)[0]+'</i>'+status())
            if weather.wind_text(w)[1] != weather.wind(in_db[1]):
                if weather.wind_text(w)[1]:
                    telebot.send_channel_message('<b>Wind has changed:</b>✅\n<i>'+weather.wind_text(w)[0]+' ('+str(w['wind_speed'])+' km/h)</i>'+status())
                else:
                    telebot.send_channel_message('<b>Wind has changed:</b>❌\n<i>'+weather.wind_text(w)[0]+' ('+str(w['wind_speed'])+' km/h, max:30km/h)</i>'+status())
        append_weather(w)
    except Exception as e:
        telebot.send_err_message('Error database-weather-change!\n\nException:\n' + str(e))

if __name__ == '__main__':
    #reset_database()
    pass