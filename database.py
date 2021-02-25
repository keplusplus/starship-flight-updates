import sqlite3, telebot, datetime, message, time

db = r'starship.db'

class Database:

    def __init__(self) -> None:
        pass

    def reset_database(self):
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

    def setup_database(self):
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

    def to_utc_time(self, time: datetime.datetime) -> datetime.datetime:
        return time + datetime.timedelta(hours=6)

    def datetime_to_string(self, dtime: datetime) -> str:
        if isinstance(dtime, datetime.time):
            return dtime.strftime('%H:%M')
        if dtime.date() == datetime.date.today():
            return dtime.strftime('%H:%M')
        return dtime.strftime('%b %d %H:%M')

    def time_to_string_local(self, time: datetime.datetime) -> str:
        return (time-datetime.timedelta(hours=6)).strftime('%H:%M')

    def sql_to_datetime(self, date: str) -> datetime.datetime:
        return datetime.datetime.strptime(date,'%Y-%m-%d %H:%M:%S')
    
    def sql_to_formatted_string(self, date: str) -> str:
        return self.time_to_string_local(self.sql_to_datetime(date))

class CameronCountyData:

    def __init__(self) -> None:
        pass

    def __not_in_past(self, date:datetime.datetime):
        return datetime.datetime.utcnow() < date

    def __is_utctoday(self, date:datetime.datetime): #true if date is today
        return datetime.datetime.utcnow().date() == date.date()

    def __utcnow_between(self, start:datetime.datetime, end:datetime.datetime):  #true if now is between start and end
        return start < datetime.datetime.utcnow() < end

    def __utctoday_or_between_not_past(self, start:datetime.datetime, end:datetime.datetime): #true if today or between
        return (self.__is_utctoday(start) or self.__is_utctoday(end) or self.__utcnow_between(start,end)) and self.__not_in_past(end)

    def __announce(self, daily_time= datetime.time(13,0), pause = datetime.timedelta(hours=6)):   #true if pause hours before daily_time or after daily
        return datetime.datetime.now().time() > daily_time or datetime.datetime.now().time() < daily_time - pause

    def __cameroncounty_valid_changes(self, sendmessage, d, in_db):   #test iv valid state changes
        if in_db['valid'] != d['valid']:    #valid has changed
            if sendmessage and self.__utctoday_or_between_not_past(d['begin'],d['end']) and (self.__announce() or in_db['announced']):
                if d['valid']:  #now valid
                    message.send_message("<a href='https://www.cameroncounty.us/spacex/'><b>Today's road closure has been rescheduled!</b></a>\n(<i>From "+ Database().datetime_to_string(d['begin'])+' to '+ Database().datetime_to_string(d['end'])+' UTC</i>)')
                else:           #no longer valid
                    message.send_message("<a href='https://www.cameroncounty.us/spacex/'><b>Today's road closure has been canceled!</b></a>\n(<i><s>From "+ Database().datetime_to_string(d['begin'])+' to '+ Database().datetime_to_string(d['end'])+'</s> UTC</i>)')

    def __cameroncounty_time_changes(self, sendmessage, d, in_db):    #test if time changes
        if d['begin'] != in_db['begin'] or d['end'] != in_db['end']:    #times have changed
            if sendmessage and (self.__utctoday_or_between_not_past(d['begin'],d['end']) or self.__utctoday_or_between_not_past(in_db['begin'],in_db['end'])) and (self.__announce() or in_db['announced']):
                d['announced'] = True
                message.send_message("<a href='https://www.cameroncounty.us/spacex/'><b>Today's road closure has changed!</b></a>\n<u>From "+ Database().datetime_to_string(d['begin'])+' to '+ Database().datetime_to_string(d['end'])+'</u> (UTC)\n⬆️\n<i>From '+ Database().datetime_to_string(in_db['begin'])+' to '+ Database().datetime_to_string(in_db['end'])+'</i> (UTC)')

    def __cameroncounty_new(self, sendmessage, d):
        if sendmessage and self.__announce() and self.__utctoday_or_between_not_past(d['begin'],d['end']):
            message.send_message('<a href="https://www.cameroncounty.us/spacex/"><b>A new road closure has been scheduled!</b></a>\n(<i>From '+ Database().datetime_to_string(d['begin'])+' to '+ Database().datetime_to_string(d['end'])+'</i> UTC)')

    def __cameroncounty_delete(self, sendmessage, in_db):
        if sendmessage and in_db['announced'] and self.__utctoday_or_between_not_past(in_db['begin'],in_db['end']):
            message.send_message('<a href="https://www.cameroncounty.us/spacex/"><b>This road closure has been removed:</b></a>\n(<i><s>From '+ Database().datetime_to_string(in_db['begin'])+' to '+ Database().datetime_to_string(in_db['end'])+'</s> UTC</i>)')

    def __cameroncounty_in_db_prepare(self, entry:list):
        return {'begin':Database().sql_to_datetime(entry[0]),'end':Database().sql_to_datetime(entry[1]),'valid':entry[2],'announced':entry[3]}

    def append_cameroncounty(self, data: list, sendmessage:bool = True):   #daily = daily update sendmessage -> does not want any changes as extra message
        conn = sqlite3.connect(db, timeout=20)
        c = conn.cursor()
        try:
            data_as_list = []   #needed to check if data in db was removed from live
            for d in data:
                d['begin'], d['end'] = Database().to_utc_time(d['begin']), Database().to_utc_time(d['end'])
                #putting live data into list to compare what is missing later
                data_as_list.append((d['begin'], d['end']))

                if c.execute('SELECT * FROM closure WHERE begin = ? OR end = ?',(d['begin'],d['end'])).fetchone():   #in database
                    #data preparation
                    in_db = self.__cameroncounty_in_db_prepare(c.execute('SELECT begin,end,valid,announced FROM closure WHERE begin = ? OR end = ?',(d['begin'],d['end'])).fetchone())
                    d['announced'] = in_db['announced']

                    #looking for changes
                    self.__cameroncounty_valid_changes(sendmessage,d,in_db)
                    self.__cameroncounty_time_changes(sendmessage,d,in_db)
                    c.execute('UPDATE closure SET begin = ?, end = ?, valid = ?, announced = ? WHERE begin = ? OR end = ?',(d['begin'],d['end'],d['valid'],d['announced'],d['begin'],d['end']))
                else:   #not in db
                    self.__cameroncounty_new(sendmessage,d)
                    announced = (not sendmessage or self.__announce()) and self.__utctoday_or_between_not_past(d['begin'],d['end'])
                    c.execute('INSERT INTO closure(begin,end,valid,announced) VALUES(?,?,?,?)',(d['begin'],d['end'],d['valid'],announced))
            if data != []:
                for in_db in c.execute('SELECT begin,end,valid,announced FROM closure WHERE valid = True').fetchall():
                    #data preparation
                    in_db = self.__cameroncounty_in_db_prepare(in_db)

                    if (in_db['begin'],in_db['end']) not in data_as_list:   #true if closure no longer on site
                        self.__cameroncounty_delete(sendmessage,in_db)
                        c.execute('DELETE FROM closure WHERE begin = ? AND end = ?',(in_db['begin'],in_db['end']))
            conn.commit()
        except Exception as e:
            telebot.send_err_message('Error database-append-closure!\n\nException:\n' + str(e)) 
    
    def road_closure_today(self, conn = None):   #for daily update
        if conn is None:
            conn = sqlite3.connect(db, timeout=20)
        c = conn.cursor()
        out = [False]
        for x in c.execute('SELECT begin, end, valid FROM closure WHERE DATE(begin) <= ? AND end >= ?',(datetime.date.today(),datetime.datetime.utcnow())).fetchall():
            if x[2]:
                out[0] = True
                out.append((Database().sql_to_datetime(x[0]),Database().sql_to_datetime(x[1]),x[2]))
        c.execute('UPDATE closure SET announced = True WHERE DATE(begin) <= ? AND end >= ?',(datetime.date.today(),datetime.datetime.utcnow()))
        conn.commit()
        return out
    
    def road_closure_active(self, conn = None):
        if conn is None: conn = sqlite3.connect(db, timeout=20)
        c = conn.cursor()
        if c.execute('SELECT * from closure WHERE begin <= Datetime("now") AND end > Datetime("now") AND valid = True').fetchone():
            in_db = c.execute('SELECT begin, end from closure WHERE begin <= Datetime("now") AND end > Datetime("now") AND valid = True').fetchall()
            out = []
            for x in in_db:
                out.append((Database().sql_to_datetime(x[0]),Database().sql_to_datetime(x[1])))
            return out
        return []

class FAAData:

    def __init__(self) -> None:
        pass

    def __not_in_past(self, date:datetime.datetime):
        return datetime.datetime.utcnow() < date

    def __is_utctoday(self, date:datetime.datetime): #true if date is today
        return datetime.datetime.utcnow().date() == date.date()

    def __utcnow_between(self, start:datetime.datetime, end:datetime.datetime):  #true if now is between start and end
        return start < datetime.datetime.utcnow() < end

    def __utctoday_or_between_not_past(self, start:datetime.datetime, end:datetime.datetime): #true if today or between
        return (self.__is_utctoday(start) or self.__is_utctoday(end) or self.__utcnow_between(start,end)) and self.__not_in_past(end)

    def __announce(self, daily_time= datetime.time(13,0), pause = datetime.timedelta(hours=6)):   #true if pause hours before daily_time or after daily
        return datetime.datetime.now().time() > daily_time or datetime.datetime.now().time() < daily_time - pause

    def __faa_altitude_changes(self, sendmessage, d, in_db):
        if sendmessage and self.__utctoday_or_between_not_past(d['begin'],d['end']) and (self.__announce() or in_db['announced']):
            if d['toAltitude'] != in_db['toAltitude']:  #test if change
                if d['toAltitude'] == -1:   #now unlimited
                    message.send_message('<a href="https://tfr.faa.gov/tfr_map_ims/html/cc/scale7/tile_33_61.html"><b>TFR max altitude has changed!</b></a>\nMax alt. is now unlimited (was '+str(in_db['toAltitude'])+'ft)\n(<i>From '+ Database().datetime_to_string(d['begin'])+' to '+ Database().datetime_to_string(d['end'])+' UTC</i>)')
                else:   #now limited
                    message.send_message('<a href="https://tfr.faa.gov/tfr_map_ims/html/cc/scale7/tile_33_61.html"><b>TFR max altitude has changed!</b></a>\nMax alt. is now '+str(d['toAltitude'])+'ft (was '+(str(in_db['toAltitude'])+' ft)').replace('-1 ft','unlimited')+'\n(<i>From '+ Database().datetime_to_string(d['begin'])+' to '+ Database().datetime_to_string(d['end'])+' UTC</i>)')

    def __faa_new(self, sendmessage, d):
        if sendmessage and self.__announce() and self.__utctoday_or_between_not_past(d['begin'],d['end']):
            if d['toAltitude'] == -1:
                message.send_message('<a href="https://tfr.faa.gov/tfr_map_ims/html/cc/scale7/tile_33_61.html"><b>New TFR has been issued!</b></a>\nMax alt.: unlimited, flight is possible!\n(<i>From '+ Database().datetime_to_string(d['begin'])+' to '+ Database().datetime_to_string(d['end'])+' UTC</i>)')
            else:
                message.send_message('<a href="https://tfr.faa.gov/tfr_map_ims/html/cc/scale7/tile_33_61.html"><b>New TFR has been issued!</b></a>\nMax alt.: '+str(d['toAltitude'])+' ft, flight is not possible!\n(<i>From '+ Database().datetime_to_string(d['begin'])+' to '+ Database().datetime_to_string(d['end'])+' UTC</i>)')

    def __faa_delete(self, sendmessage, in_db):
        if sendmessage and in_db['announced'] and self.__utctoday_or_between_not_past(in_db['begin'],in_db['end']):
            message.send_message('<a href="https://tfr.faa.gov/tfr_map_ims/html/cc/scale7/tile_33_61.html"><b>This TFR has been removed:</b></a>\n(<i><s>From '+ Database().datetime_to_string(in_db['begin'])+' to '+ Database().datetime_to_string(in_db['end'])+'</s> UTC</i>)')

    def __faa_in_db_prepare(self, entry:list):
        return {'begin':Database().sql_to_datetime(entry[0]),'end':Database().sql_to_datetime(entry[1]),'toAltitude':entry[2],'announced':entry[3]}

    def append_faa(self, data, sendmessage:bool = True, daily_time:datetime.datetime = datetime.time(13,0)):
        conn = sqlite3.connect(db, timeout=20)
        c = conn.cursor()
        #try:
        data_as_list = []   #needed to check if data in db was removed from live
        for d in data:
            data_as_list.append((d['begin'], d['end']))
            if c.execute('SELECT * FROM faa WHERE begin = ? AND end = ?',(d['begin'], d['end'])).fetchone():   #in db
                #changed faa
                in_db = self.__faa_in_db_prepare(c.execute('SELECT begin,end,toAltitude,announced FROM faa WHERE begin = ? AND end = ?',(d['begin'], d['end'])).fetchone())
                self.__faa_altitude_changes(sendmessage,d,in_db)
                c.execute('UPDATE faa SET fromSurface = ?, toAltitude = ? WHERE begin = ? AND end = ?',(d['fromSurface'],d['toAltitude'],d['begin'], d['end']))
            else:   #not in db
                #new faa
                self.__faa_new(sendmessage,d)
                announced = (not sendmessage or self.__announce()) and self.__utctoday_or_between_not_past(d['begin'],d['end'])
                c.execute('INSERT INTO faa(begin,end,fromSurface,toAltitude,announced) VALUES(?,?,?,?,?)',(d['begin'],d['end'],d['fromSurface'],d['toAltitude'],announced))
        #deleted faa
        if data != []:
            for in_db in c.execute('SELECT begin,end,toAltitude,announced FROM faa').fetchall():
                #data preparation
                in_db = self.__faa_in_db_prepare(in_db)

                if (in_db['begin'],in_db['end']) not in data_as_list:
                    self.__faa_delete(sendmessage, in_db)
                    c.execute('DELETE FROM faa WHERE begin = ? AND end = ?',(in_db['begin'],in_db['end']))
        conn.commit()
        #except Exception as e:
        #    telebot.send_err_message('Error database-append-faa!\n\nException:\n' + str(e))

    def faa_today(self, conn = None):
        if conn is None:
            conn = sqlite3.connect(db, timeout=20)
        c = conn.cursor()
        out = [False]
        for in_db in c.execute('SELECT begin, end, toAltitude FROM faa WHERE DATE(begin) <= ? AND end >= ?',(datetime.date.today(),datetime.datetime.utcnow())).fetchall():
            if in_db[2] == -1:
                out[0] = True
                out.append((Database().sql_to_datetime(in_db[0]),Database().sql_to_datetime(in_db[1]),in_db[2],True))
            else:
                out.append((Database().sql_to_datetime(in_db[0]),Database().sql_to_datetime(in_db[1]),in_db[2],False))
        c.execute('UPDATE faa SET announced = TRUE WHERE DATE(begin) <= ? AND end >= ?',(datetime.date.today(),datetime.datetime.utcnow()))
        conn.commit()
        return out

    def faa_active(self, conn = None):
        if conn is None: conn = sqlite3.connect(db, timeout=20)
        c = conn.cursor()
        if c.execute('SELECT * from faa WHERE begin <= Datetime("now") AND end > Datetime("now") AND toAltitude = -1').fetchone():
            in_db = c.execute('SELECT begin, end from faa WHERE begin <= Datetime("now") AND end > Datetime("now") AND toAltitude = -1').fetchall()
            out = []
            for x in in_db:
                out.append((Database().sql_to_datetime(x[0]),Database().sql_to_datetime(x[1])))
            return out
        return []

class WikiData:

    def __init__(self) -> None:
        pass

    def compareDicts(self, new:dict, old:dict) -> dict:
        out = {}
        if new.keys() == old.keys():
            for x in new:
                if new[x] != old[x]:
                    out[x] = [new[x],old[x]]
        return out

    def append_history(self, data:list):
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
                        message.send_test_message(message.history_message(d, self.compareDicts(d,old)))
                        time.sleep(3)
                    elif old['status'] != d['status'] and d['status'] not in ['Retired','Destroyed','Scrapped','Suspended']:    #-> message if status changed from retired/destroyed/scrapped to something else than retired/destroyed/scrapped
                        message.send_test_message(message.history_message(d, self.compareDicts(d,old)))
                        time.sleep(3)
            else:   #not in db
                message.send_test_message(message.history_message(d))
                c.execute('INSERT INTO history(name,firstSpotted,rolledOut,firstStaticFire,maidenFlight,decomissioned,constructionSite,status,flights) VALUES(?,?,?,?,?,?,?,?,?)',(d['name'],d['firstSpotted'],d['rolledOut'],d['firstStaticFire'],d['maidenFlight'],d['decomissioned'],d['constructionSite'],d['status'],d['flights']))
                time.sleep(5)
            conn.commit()