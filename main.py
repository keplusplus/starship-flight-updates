import database
from data_sources import weather
#Gather current data -> every morning
#schedule event[closure/faa] -> when new data
#when schedulued task event: test if event still active: send tel message
#when event active: look for extra data[plane/stream/tweet]


def daily_update(): #once a day
    #update all data like closure, faa...
    w = weather.today_forecast()
    print(weather.weather_text(w))
    print(str(weather.wind_text(w))+' ('+str(w['wind_speed'])+' km/h)')
    if database.road_closure_today():
        print(database.road_closure_today())

def regular_update():
    #only allowd to run frequently after the daily_update
    #since otherwise we would get an updated weather/closure
    #before it would be anounced!
    pass

#daily_update()