import database,telebot
from data_sources import weather
from data_sources.cameron_county import CameronCountyParser
#Gather current data -> every morning
#schedule event[closure/faa] -> when new data
#when schedulued task event: test if event still active: send tel message
#when event active: look for extra data[plane/stream/tweet]


def daily_update(): #every boca morning
    ccp = CameronCountyParser()
    ccp.parse()
    database.append_cameroncounty(ccp.closures,True)

    w = weather.today_forecast()

    flight = (weather.weather_text(w)[1] and weather.wind_text(w)[1] and bool(database.road_closure_today()[2])) #faa missing
    staticfire = bool(database.road_closure_today()[2])
    out = '<u><b>Daily Update</b></u>\n<a href="https://www.cameroncounty.us/spacex/"><b>Road Closure:</b></a>'
    if database.road_closure_today():
        out+= '✅\nfrom '+database.datetime_to_string(database.road_closure_today()[0])+' to '+database.datetime_to_string(database.road_closure_today()[1])+' (UTC)'
        out+= '\n<i>(local: '+database.datetime_to_string(database.road_closure_today(True)[0])+' to '+database.datetime_to_string(database.road_closure_today(True)[1])+')</i>\n'
    else:
        out+= '❌\nnothing scheduled'
    #out+='<b>FAA</b>:❓\n<code>data missing</code>\n'
    out+='<a href="https://openweathermap.org/city/4720060"><b>Weather today:</b></a>'
    if weather.weather_text(w)[1]:
        out+='✅\n'+weather.weather_text(w)[0]+'\n'
    else:
        out+='❌\n'+weather.weather_text(w)[0]+'\n'
    out+='<a href="https://openweathermap.org/city/4720060"><b>Wind:</b></a>'
    if weather.wind_text(w)[1]:
        out+='✅\n'+weather.wind_text(w)[0]+' ('+str(w['wind_speed'])+' km/h)\n'
    else:
        out+='❌\n'+weather.wind_text(w)[0]+' ('+str(w['wind_speed'])+' km/h, max:30km/h)\n'
    if flight:
        out+='\nFlight is possible today🚀\n'
    elif staticfire:
        out+='\nStatic fire or wdr are possible today\n'
    else:
        out+='\nNothing big happening today on current data\n'
    out+='<i>(We will keep you updated if anything changes!)</i>'
    print(out)
    print(telebot.send_channel_message(out, True))

def regular_update():
    #if time is before daily_update schedule daily needs to be set to True
    #w = weather.current_weather()
    pass

def main():
    daily_update()  #needs to be scheduled once a day

if __name__ == "__main__":
    main()