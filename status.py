import database
from data_sources import weather

class Status:

    _last_status = {'flight':None,'static':None}
    _last_active_status = {'flight':False,'static':False}

    def __init__(self):
        pass

    def status(self, daily = False, weather_data = None):    #returns (flight:bool, static:bool)
        CameronCountyData, FAAData = database.CameronCountyData, database.FAAData
        if daily:
            if weather_data is None: weather_data = weather.Weather().today_forecast()
            return (weather.Weather().wind_text(weather_data)[1] and weather.Weather().wind_text(weather_data)[1] and (CameronCountyData().road_closure_today()[0]) and (FAAData().faa_today()[0])), (CameronCountyData().road_closure_today()[0])
        return (weather.Weather().wind_text(weather.Weather().current_weather())[1] and weather.Weather().wind_text(weather.Weather().current_weather())[1] and (CameronCountyData().road_closure_active() != []) and (FAAData().faa_active() != [])), (CameronCountyData().road_closure_active() != [])

    def daily_status(self, w) -> str:  #called by min-daily
        out = ''
        flight, static = self.status(True, w)
        if flight:
            out+='\n<u><b>Flight is possible today</b></u>🚀✅\nStatic fire or wdr are also possible\n'
        else:
            out+='\n<u><b>Presumably no flight today</b></u>🚀❌\n'
        if static:
            if not flight:
                out+='Static fire or wdr are possible\n'
        else:
            out+='Nothing big happening on current data❗\n'
        return out

    def value_change_status(self, conn) -> str:   #called when new/change/remove closure/tfr
        return ''
        if database.road_closure_active(conn=conn) != [] or database.faa_active(conn=conn) != []:
            return ''
        flight = weather.Weather().weather_text(weather.Weather().current_weather())[1] and weather.Weather().wind_text(weather.Weather().current_weather())[1] and database.road_closure_today(conn)[0] and database.faa_today(conn)[0]
        static = database.road_closure_today(conn)[0]
        out = ''
        return out
    
    def active_change(self, currently_active) -> str:
        out = '\n\nStatus: '
        flight, static = self.status()
        weather_data, wind_data = weather.Weather().weather_text(weather.Weather().current_weather())[1], weather.Weather().wind_text(weather.Weather().current_weather())[1]
        if Status()._last_active_status['flight'] != flight or Status()._last_active_status['static'] != static:   #status change
            out +='<i>(changed!)</i>\n'
        else:
            out +='<i>(not changed)</i>\n'
        if currently_active['closure'] != [] and currently_active['tfr'] != []:
            if not weather_data and wind_data:    #bad weather & no wind
                out += '<u>Flight is not possible due to weather!</u>🚀❌\nStatic fire or wdr are still possible<i>\nWeather: '+weather.Weather().weather_text(weather.Weather().current_weather())[0]+'</i>'
            elif weather_data and not wind_data:     #too windy & good weather
                out += '<u>Flight is not possible due to wind!</u>🚀❌\nStatic fire or wdr are still possible<i>\nWind: '+weather.Weather().wind_text(weather.Weather().current_weather())[0]+'</i>'
            elif not weather_data and not wind_data:    #bad weather & wind
                out += '<u>Flight is not possible due to weather and wind!</u>🚀❌\nStatic fire or wdr are still possible<i>\nWeather: '+weather.Weather().weather_text(weather.Weather().current_weather())[0]+'\nWind: '+weather.Weather().wind_text(weather.Weather().current_weather())[0]+'</i>'
            else:   #good weather & no wind
                out += '<u><b>Flight is now possible</b></u>🚀✅'
        elif currently_active['closure'] != [] and currently_active['tfr'] == []:
            if Status()._last_active_status['flight']:
                out += '<u>Flight is no longer possible!</u>🚀❌\nStatic fire or wdr are still possible!'
            else:
                out += '<u>Static fire or wdr are now possible!</u>🔥✅'
        else:
            if Status()._last_active_status['flight']:
                out+='<u>Flight is no longer possible!</u>🚀❌\nNothing is now possible!'
            elif Status()._last_active_status['static']:
                out+='<u>Static fire or wdr are no longer possible!</u>🔥❌\nNothing is now possible!'
            else:
                out += '<u>Nothing is currently possible!❌</u>'
        Status()._last_active_status['flight'], Status()._last_active_status['static'] = flight, static
        return out