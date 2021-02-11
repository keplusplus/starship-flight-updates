import database,telebot,datetime,time, schedule, active
from status import Status
from data_sources.weather import Weather
from data_sources.cameron_county import CameronCountyParser
from data_sources.faa import FAAParser
#Gather current data -> every morning
#schedule event[closure/faa] -> when new data
#when schedulued task event: test if event still active: send tel message
#when event active: look for extra data[plane/stream/tweet]


def daily_update(): #every boca morning
    print('>daily')
    try:
        ccp = CameronCountyParser()
        ccp.parse()
        database.append_cameroncounty(ccp.closures,False)
        faa = FAAParser()
        faa.parse()
        database.append_faa(faa.tfrs,False)
        w = Weather().today_forecast()
        if w == {}:
            return
        print('>collected & waiting')
        #make sure the message is sent exactly at 13:00
        if (datetime.datetime.now().replace(hour=13,minute=0,second=0,microsecond=0)-datetime.datetime.now()).total_seconds() > 0:
            time.sleep((datetime.datetime.now().replace(hour=13,minute=0,second=0,microsecond=0)-datetime.datetime.now()).total_seconds())
        flight = (Weather().weather_text(w)[1] and Weather().wind_text(w)[1] and bool(database.road_closure_today()[0]) and database.faa_today()[0])
        staticfire = bool(database.road_closure_today()[0])
        #Header & Roadclosure
        out = '<b>𝗗𝗮𝗶𝗹𝘆 𝗨𝗽𝗱𝗮𝘁𝗲</b><i> (local time '+database.datetime_to_string(datetime.datetime.utcnow()-datetime.timedelta(hours=6))+')</i>\n<a href="https://www.cameroncounty.us/spacex/"><b>Road Closure:</b></a>'
        if database.road_closure_today()[0]:
            out+= '✅\n'
            for x in database.road_closure_today()[1:]:
                out+= 'from '+database.datetime_to_string(x[0])+' to '+database.datetime_to_string(x[1])+' (UTC)'
                out+= '\n<i>(local: '+database.datetime_to_string(x[0]-datetime.timedelta(hours=6))+' to '+database.datetime_to_string(x[1]-datetime.timedelta(hours=6))+')</i>\n'
        else:
            out+= '❌\nnothing scheduled!\n'
        #TFR
        out+='<a href="https://tfr.faa.gov/tfr_map_ims/html/cc/scale7/tile_33_61.html"><b>TFR:</b></a>'
        if database.faa_today()[0]:
            out+='✅\n'
        else:
            out+='❌\n'
            if len(database.faa_today()) != 1:
                out+='(max alt. needs to be unlimited for flight)\n'
        unlimited, limited = False, False
        for x in database.faa_today()[1:]:
            if x[3]:
                unlimited = True
                out+='from '+database.datetime_to_string(x[0])+' to '+database.datetime_to_string(x[1])+' (max alt.: unlimited)\n'
                out+='<i>(local from '+database.datetime_to_string(x[0]-datetime.timedelta(hours=6))+' to '+database.datetime_to_string(x[1])+')</i>\n'
            else:
                limited = True
        if unlimited and limited:
            out+='-----\n'
        for x in database.faa_today()[1:]:
            if not x[3]:
                out+='<i>from '+database.datetime_to_string(x[0])+' to '+database.datetime_to_string(x[1])+' (max alt.: '+str(x[2])+' ft)</i>\n'
        #Weather
        out+='<a href="https://openweathermap.org/city/4720060"><b>Weather today:</b></a>'
        if Weather().weather_text(w)[1]:
            out+='✅\n'+Weather().weather_text(w)[0]+'\n'
        else:
            out+='❌\n'+Weather().weather_text(w)[0]+'\n'
        #Wind
        out+='<a href="https://openweathermap.org/city/4720060"><b>Wind:</b></a>'
        if Weather().wind_text(w)[1]:
            out+='✅\n'+Weather().wind_text(w)[0]+'\n'
        else:
            out+='❌\n'+Weather().wind_text(w)[0]+'\n'
        #Flight Message
        out += Status().daily_status(w)
        out+='<i>(We will keep you updated if anything changes!)</i>'
        telebot.send_channel_message(out, True)
        database.announce_today_closures()
        database.announce_today_faas()
    except Exception as e:
        telebot.send_err_message('Error daily-message!\n\nException:\n' + str(e))

def regular_update():
    print('>updating')
    try:
        ccp = CameronCountyParser()
        ccp.parse()
        #ccp.closures.append({'begin': datetime.datetime(2021,2,9,15,28),'end': datetime.datetime(2021,2,9,15,30),'valid': True})
        database.append_cameroncounty(ccp.closures)

        faa = FAAParser()
        faa.parse()
        #faa.tfrs.append({'begin':datetime.datetime(2021,2,9,21,27),'end':datetime.datetime(2021,2,9,21,29),'fromSurface':True,'toAltitude':-1})
        database.append_faa(faa.tfrs)
    except Exception as e:
        telebot.send_err_message('Error regular-update!\n\nException:\n' + str(e))

#database.reset_database()
def main():
    database.setup_database()
    regular_update()
    active.start()
    schedule.every().day.at("12:55").do(daily_update)
    schedule.every(15).to(25).minutes.do(regular_update)
    print('>starting main-main loop')
    while 1:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()