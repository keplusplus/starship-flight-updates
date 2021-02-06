import database,telebot,datetime,time, schedule
from data_sources import weather
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

        w = weather.today_forecast()
        database.append_weather(w)
        print('>collected & waiting')
        #make sure the message is sent exactly at 13:00
        time.sleep((datetime.datetime.now().replace(hour=13,minute=0,second=0,microsecond=0)-datetime.datetime.now()).total_seconds())
        flight = (weather.weather_text(w)[1] and weather.wind_text(w)[1] and bool(database.road_closure_today()[0]) and database.faa_today()[0])
        staticfire = bool(database.road_closure_today()[0])
        #Header & Roadclosure
        out = '<b>𝗗𝗮𝗶𝗹𝘆 𝗨𝗽𝗱𝗮𝘁𝗲</b><i> (local time '+database.datetime_to_string(datetime.datetime.now()-datetime.timedelta(hours=7))+')</i>\n<a href="https://www.cameroncounty.us/spacex/"><b>Road Closure:</b></a>'
        if database.road_closure_today()[0]:
            out+= '✅\n'
            for x in database.faa_today()[1:]:
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
        for x in database.faa_today()[1:]:
            if x[3]:
                out+='from '+database.datetime_to_string(x[0])+' to '+database.datetime_to_string(x[1])+' (max alt.: '+str(x[2])+' ft)\n'
                out+='<i>(local from '+database.datetime_to_string(x[0]-datetime.timedelta(hours=6))+' to '+database.datetime_to_string(x[1])+')\n'
        for x in database.faa_today()[1:]:
            if not x[3]:
                out+='<i>from '+database.datetime_to_string(x[0])+' to '+database.datetime_to_string(x[1])+' (max alt.: '+str(x[2])+' ft)</i>\n'
        #Weather
        out+='<a href="https://openweathermap.org/city/4720060"><b>Weather today:</b></a>'
        if weather.weather_text(w)[1]:
            out+='✅\n'+weather.weather_text(w)[0]+'\n'
        else:
            out+='❌\n'+weather.weather_text(w)[0]+'\n'
        #Wind
        out+='<a href="https://openweathermap.org/city/4720060"><b>Wind:</b></a>'
        if weather.wind_text(w)[1]:
            out+='✅\n'+weather.wind_text(w)[0]+' ('+str(w['wind_speed'])+' km/h)\n'
        else:
            out+='❌\n'+weather.wind_text(w)[0]+' ('+str(w['wind_speed'])+' km/h, max:30km/h)\n'
        #Flight Message
        if flight:
            out+='\n<u><b>Flight is possible today</b></u>🚀✅\n'
        else:
            out+='\n<u><b>Presumably no flight today</b></u>🚀❌\n'
        if staticfire:
            out+='Static fire or wdr are still possible\n'
        else:
            out+='Nothing big happening on current data\n'
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
        database.append_cameroncounty(ccp.closures)

        faa = FAAParser()
        faa.parse()
        database.append_faa(faa.tfrs)
        database.weather_change(weather.current_weather())
    except Exception as e:
        telebot.send_err_message('Error regular-update!\n\nException:\n' + str(e))

def main():
    schedule.every().day.at("12:55").do(daily_update)
    schedule.every(15).to(25).minutes.do(regular_update)
    
    while 1:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()