import sqlite3, telebot, datetime, message, time
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
    c.execute('DROP TABLE history')
    c.execute("CREATE TABLE 'history' ('name' VARCHAR(250) PRIMARY KEY,'firstSpotted' VARCHAR(250) NOT NULL,'rolledOut' VARCHAR(250) NOT NULL,'firstStaticFire' VARCHAR(250) NOT NULL,'maidenFlight' VARCHAR(250) NOT NULL,'decomissioned' VARCHAR(250) NOT NULL,'constructionSite' VARCHAR(250) NOT NULL,'status' VARCHAR(250) NOT NULL,'flights' INTEGER NOT NULL);")
    conn.commit()

def setup_database():
    print('setting up db')
    conn = sqlite3.connect(db, timeout=20)
    c = conn.cursor()
    try:
        c.execute("CREATE TABLE 'closure' ('id' INTEGER PRIMARY KEY AUTOINCREMENT,'begin' TIMESTAMP NOT NULL,'end' TIMESTAMP NOT NULL,'valid' BOOL, 'announced' BOOL DEFAULT FALSE);")
    except:pass
    try:
        c.execute("CREATE TABLE 'faa' ('id' INTEGER PRIMARY KEY AUTOINCREMENT,'begin' TIMESTAMP NOT NULL,'end' TIMESTAMP NOT NULL,'fromSurface' BOOL, toAltitude INTEGER, 'announced' BOOL DEFAULT FALSE);")
    except:pass
    try:
        c.execute("CREATE TABLE 'history' ('name' VARCHAR(250) PRIMARY KEY,'firstSpotted' VARCHAR(250) NOT NULL,'rolledOut' VARCHAR(250) NOT NULL,'firstStaticFire' VARCHAR(250) NOT NULL,'maidenFlight' VARCHAR(250) NOT NULL,'decomissioned' VARCHAR(250) NOT NULL,'constructionSite' VARCHAR(250) NOT NULL,'status' VARCHAR(250) NOT NULL,'flights' INTEGER NOT NULL);")
    except:pass
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

def road_closure_active(conn = None):  #used by thread
    if conn is None: conn = sqlite3.connect(db, timeout=20)
    c = conn.cursor()
    if c.execute('SELECT * from closure WHERE begin <= Datetime("now") AND end > Datetime("now") AND valid = True').fetchone():
        in_db = c.execute('SELECT begin, end from closure WHERE begin <= Datetime("now") AND end > Datetime("now") AND valid = True').fetchall()
        out = []
        for x in in_db:
            out.append((sql_to_datetime(x[0]),sql_to_datetime(x[1])))
        return out
    return []

def faa_active(conn = None):  #in last min
    if conn is None: conn = sqlite3.connect(db, timeout=20)
    c = conn.cursor()
    if c.execute('SELECT * from faa WHERE begin <= Datetime("now") AND end > Datetime("now") AND toAltitude = -1').fetchone():
        in_db = c.execute('SELECT begin, end from faa WHERE begin <= Datetime("now") AND end > Datetime("now") AND toAltitude = -1').fetchall()
        out = []
        for x in in_db:
            out.append((sql_to_datetime(x[0]),sql_to_datetime(x[1])))
        return out
    return []

def __not_in_past(date:datetime.datetime):
    return datetime.datetime.utcnow() < date

def __is_utctoday(date:datetime.datetime): #true if date is today
    return datetime.datetime.utcnow().date() == date.date()

def __utcnow_between(start:datetime.datetime, end:datetime.datetime):  #true if now is between start and end
    return start < datetime.datetime.utcnow() < end

def __utctoday_or_between(start:datetime.datetime, end:datetime.datetime): #true if today or between
    return (__is_utctoday(start) or __is_utctoday(end) or __utcnow_between(start,end)) and __not_in_past(end)

def __announce(daily_time= datetime.time(13,0), pause = datetime.timedelta(hours=10)):   #true if pause hours before daily_time or after daily
    return datetime.datetime.now().time() > daily_time or datetime.datetime.now().time() < daily_time - pause

def __cameroncounty_valid_changes(sendmessage, d, in_db):   #test iv valid state changes
    if in_db['valid'] != d['valid']:    #valid has changed
        if sendmessage and __utctoday_or_between(d['begin'],d['end']) and (__announce() or in_db['announced']):
            if d['valid']:  #now valid
                message.send_message("<a href='https://www.cameroncounty.us/spacex/'><b>Today's road closure has been rescheduled!</b></a>\n(<i>From "+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+' UTC</i>)')
            else:           #no longer valid
                message.send_message("<a href='https://www.cameroncounty.us/spacex/'><b>Today's road closure has been canceled!</b></a>\n(<i><s>From "+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+'</s> UTC</i>)')

def __cameroncounty_time_changes(sendmessage, d, in_db):    #test if time changes
    if d['begin'] != in_db['begin'] or d['end'] != in_db['end']:    #times have changed
        if sendmessage and (__utctoday_or_between(d['begin'],d['end']) or __utctoday_or_between(in_db['begin'],in_db['end'])) and (__announce() or in_db['announced']):
            d['announced'] = True
            message.send_message("<a href='https://www.cameroncounty.us/spacex/'><b>Today's road closure has changed!</b></a>\n<u>From "+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+'</u> (UTC)\n⬆️\n<i>From '+datetime_to_string(in_db['begin'])+' to '+datetime_to_string(in_db['end'])+'</i> (UTC)')

def __cameroncounty_changes(sendmessage, d, in_db):
    __cameroncounty_valid_changes(sendmessage,d,in_db)
    __cameroncounty_time_changes(sendmessage,d,in_db)

def __cameroncounty_new(sendmessage, d):
    if sendmessage and __announce() and __utctoday_or_between(d['begin'],d['end']):
        message.send_message('<a href="https://www.cameroncounty.us/spacex/"><b>A new road closure has been scheduled!</b></a>\n(<i>From '+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+'</i> UTC)')

def __cameroncounty_delete(sendmessage, in_db):
    if sendmessage and in_db['announced'] and __utctoday_or_between(in_db['begin'],in_db['end']):
        message.send_message('<a href="https://www.cameroncounty.us/spacex/"><b>This road closure has been removed:</b></a>\n(<i><s>From '+datetime_to_string(in_db['begin'])+' to '+datetime_to_string(in_db['end'])+'</s> UTC</i>)')

def append_cameroncounty(data: list, sendmessage:bool = True, daily_time:datetime.datetime = datetime.time(13,0)):   #daily = daily update sendmessage -> does not want any changes as extra message
    conn = sqlite3.connect(db, timeout=20)
    c = conn.cursor()
    try:
        data_as_list = []   #needed to check if data in db was removed from live
        for d in data:
            d['begin'], d['end'] = to_utc_time(d['begin']), to_utc_time(d['end'])
            #putting live data into list to compare what is missing later
            data_as_list.append((d['begin'], d['end']))

            if c.execute('SELECT * FROM closure WHERE begin = ? OR end = ?',(d['begin'],d['end'])).fetchone():   #in database
                #data preparation
                in_db = c.execute('SELECT begin,end,valid,announced FROM closure WHERE begin = ? OR end = ?',(d['begin'],d['end'])).fetchone()
                in_db = {'begin':sql_to_datetime(in_db[0]),'end':sql_to_datetime(in_db[1]),'valid':in_db[2],'announced':in_db[3]}
                d['announced'] = in_db['announced']

                #testing for changes
                __cameroncounty_changes(sendmessage, d, in_db)
                c.execute('UPDATE closure SET begin = ?, end = ?, valid = ?, announced = ? WHERE begin = ? OR end = ?',(d['begin'],d['end'],d['valid'],d['announced'],d['begin'],d['end']))
            else:   #not in db
                __cameroncounty_new(sendmessage,d)
                announced = (not sendmessage or __announce()) and __utctoday_or_between(d['begin'],d['end'])
                c.execute('INSERT INTO closure(begin,end,valid,announced) VALUES(?,?,?,?)',(d['begin'],d['end'],d['valid'],announced))
        if data != []:
            for in_db in c.execute('SELECT begin,end,valid,announced FROM closure WHERE valid = True').fetchall():
                #data preparation
                in_db = {'begin':sql_to_datetime(in_db[0]),'end':sql_to_datetime(in_db[1]),'valid':in_db[2],'announced':in_db[3]}

                if (in_db['begin'],in_db['end']) not in data_as_list:   #true if closure no longer on site
                    __cameroncounty_delete(sendmessage,in_db)
                    c.execute('DELETE FROM closure WHERE begin = ? AND end = ?',(in_db['begin'],in_db['end']))
        conn.commit()
    except Exception as e:
        telebot.send_err_message('Error database-append-closure!\n\nException:\n' + str(e)) 

def announce_today_closures():
    conn = sqlite3.connect(db, timeout=20)
    c = conn.cursor()
    c.execute('UPDATE closure SET announced = TRUE WHERE DATE(begin) = ? OR DATE(end) = ?',(datetime.date.today(),datetime.date.today()))
    conn.commit()

def append_faa(data, sendmessage:bool = True, daily_time:datetime.datetime = datetime.time(13,0)):
    conn = sqlite3.connect(db, timeout=20)
    c = conn.cursor()
    try:
        data_as_list = []   #needed to check if data in db was removed from live
        for d in data:
            data_as_list.append((d['begin'], d['end']))
            if c.execute('SELECT * FROM faa WHERE begin = ? AND end = ?',(d['begin'], d['end'])).fetchone():   #in db
                #changed faa
                in_db = c.execute('SELECT begin,end,fromSurface,toAltitude,announced FROM faa WHERE begin = ? AND end = ?',(d['begin'], d['end'])).fetchone()
                if sendmessage and in_db[4]:
                    if in_db[2] != d['fromSurface'] and in_db[3] != d['toAltitude']:
                        message.send_message('<a href="https://tfr.faa.gov/tfr_map_ims/html/cc/scale7/tile_33_61.html"><b>FromSurface and max. alt have changed to:</b></a>\n'+str(d['fromSurface'])+' and '+str(d['toAltitude']).replace('-1','unlimited')+' ft'+Status().value_change_status(conn))
                    elif in_db[2] != d['fromSurface']:
                        message.send_message('<a href="https://tfr.faa.gov/tfr_map_ims/html/cc/scale7/tile_33_61.html"><b>FromSurface has changed to: '+str(d['fromSurface'])+'</b></a>'+Status().value_change_status(conn))
                    elif in_db[3] != d['toAltitude']:
                        if d['toAltitude'] == -1:
                            message.send_message('<a href="https://tfr.faa.gov/tfr_map_ims/html/cc/scale7/tile_33_61.html"><b>TFR max altitude has changed!</b></a>\nMax alt. is now unlimited (was '+str(in_db[3])+'ft)\n(<i>From '+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+' UTC</i>)'+Status().value_change_status(conn))
                        else:
                            was = str(in_db[3])
                            if in_db[3] == -1:
                                was = 'unlimited'
                            message.send_message('<a href="https://tfr.faa.gov/tfr_map_ims/html/cc/scale7/tile_33_61.html"><b>TFR max altitude has changed!</b></a>\nMax alt. is now '+str(d['toAltitude'])+'ft (was '+was+' ft)\n(<i>From '+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+' UTC</i>)'+Status().value_change_status(conn))
                c.execute('UPDATE faa SET fromSurface = ?, toAltitude = ? WHERE begin = ? AND end = ?',(d['fromSurface'],d['toAltitude'],d['begin'], d['end']))
            else:   #not in db
                #new faa
                announced = False
                if datetime.datetime.now().time() > daily_time and d['begin'].date() <= datetime.date.today() and d['end'] > datetime.datetime.utcnow():
                    announced = True
                c.execute('INSERT INTO faa(begin,end,fromSurface,toAltitude,announced) VALUES(?,?,?,?,?)',(d['begin'],d['end'],d['fromSurface'],d['toAltitude'],announced))
                if sendmessage and announced:
                    if d['toAltitude'] == -1:
                        message.send_message('<a href="https://tfr.faa.gov/tfr_map_ims/html/cc/scale7/tile_33_61.html"><b>New TFR has been issued!</b></a>\nMax alt.: unlimited, flight is possible!\n(<i>From '+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+' UTC</i>)'+Status().value_change_status(conn))
                    else:
                        message.send_message('<a href="https://tfr.faa.gov/tfr_map_ims/html/cc/scale7/tile_33_61.html"><b>New TFR has been issued!</b></a>\nMax alt.: '+str(d['toAltitude'])+' ft, flight is not possible!\n(<i>From '+datetime_to_string(d['begin'])+' to '+datetime_to_string(d['end'])+' UTC</i>)'+Status().value_change_status(conn))
        #deleted faa
        if data != []:
            for in_db in c.execute('SELECT begin, end, announced FROM faa').fetchall():
                if (sql_to_datetime(in_db[0]),sql_to_datetime(in_db[1])) not in data_as_list:
                    if sendmessage and (((sql_to_datetime(in_db[0]) <= datetime.datetime.utcnow() <= sql_to_datetime(in_db[1])) or (in_db[2] and sql_to_datetime(in_db[0]).date() == datetime.datetime.utcnow().date() and sql_to_datetime(in_db[0]) > datetime.datetime.utcnow()))):
                        message.send_message('<a href="https://tfr.faa.gov/tfr_map_ims/html/cc/scale7/tile_33_61.html"><b>This TFR has been removed:</b></a>\n(<i><s>From '+datetime_to_string(sql_to_datetime(in_db[0]))+' to '+datetime_to_string(sql_to_datetime(in_db[1]))+'</s> UTC</i>)'+Status().value_change_status(conn))
                    c.execute('DELETE FROM faa WHERE begin = ? AND end = ?',(sql_to_datetime(in_db[0]),sql_to_datetime(in_db[1])))
        conn.commit()
    except Exception as e:
        telebot.send_err_message('Error database-append-faa!\n\nException:\n' + str(e))

def announce_today_faas():
    conn = sqlite3.connect(db, timeout=20)
    c = conn.cursor()
    c.execute('UPDATE faa SET announced = TRUE WHERE DATE(begin) = ? OR DATE(end) = ?',(datetime.date.today(),datetime.date.today()))
    conn.commit()

def compareDicts(new:dict, old:dict) -> dict:
    out = {}
    if new.keys() == old.keys():
        for x in new:
            if new[x] != old[x]:
                out[x] = [new[x],old[x]]
    return out

def append_history(data:list):
    conn = sqlite3.connect(db, timeout=20)
    c = conn.cursor()
    for d in data:
        if c.execute('SELECT * FROM history WHERE name = ?',(d['name'],)).fetchone():   #in db -> look for changes
            in_db = c.execute('SELECT * FROM history WHERE name = ?',(d['name'],)).fetchone()
            if list(set(list(d.values()))-set(in_db)) != []:
                #something changed
                old = {'name':in_db[0],'firstSpotted':in_db[1],'rolledOut':in_db[2],'firstStaticFire':in_db[3],'maidenFlight':in_db[4],'decomissioned':in_db[5],'constructionSite':in_db[6],'status':in_db[7],'flights':in_db[8]}
                c.execute('UPDATE history SET firstSpotted = ?,rolledOut = ?, firstStaticFire = ?, maidenFlight = ?, decomissioned = ?, constructionSite = ?, status = ?, flights = ? WHERE name = ?',(d['firstSpotted'],d['rolledOut'],d['firstStaticFire'],d['maidenFlight'],d['decomissioned'],d['constructionSite'],d['status'],d['flights'],d['name']))
                if old['status'] not in ['Retired','Destroyed','Scrapped','Suspended']: #-> no message for retired/destroyed/scrapped starships
                    message.send_test_message(message.history_message(d, compareDicts(d,old)))
                    time.sleep(3)
                elif old['status'] != d['status'] and d['status'] not in ['Retired','Destroyed','Scrapped','Suspended']:    #-> message if status changed from retired/destroyed/scrapped to something else than retired/destroyed/scrapped
                    message.send_test_message(message.history_message(d, compareDicts(d,old)))
                    time.sleep(3)
        else:   #not in db
            message.send_test_message(message.history_message(d))
            c.execute('INSERT INTO history(name,firstSpotted,rolledOut,firstStaticFire,maidenFlight,decomissioned,constructionSite,status,flights) VALUES(?,?,?,?,?,?,?,?,?)',(d['name'],d['firstSpotted'],d['rolledOut'],d['firstStaticFire'],d['maidenFlight'],d['decomissioned'],d['constructionSite'],d['status'],d['flights']))
            time.sleep(5)
        conn.commit()