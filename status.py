import database
from data_sources import weather

class Status:

    _last_status = {'flight':None,'static':None}
    _last_active_status = {'flight':None,'static':None}

    def __init__(self):
        pass

    def daily_status(self, w) -> str:  #called by min-daily
        CameronCountyData, FAAData = database.CameronCountyData, database.FAAData
        out = ''
        flight = weather.Weather().weather_text(w)[1] and weather.Weather().wind_text(w)[1] and CameronCountyData().road_closure_today()[0] and FAAData().faa_today()[0]
        staticfire = CameronCountyData().road_closure_today()[0]
        if flight:
            out+='\n<u><b>Flight is possible today</b></u>🚀✅\nStatic fire or wdr are also possible\n'
        else:
            out+='\n<u><b>Presumably no flight today</b></u>🚀❌\n'
        if staticfire:
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
        return ''
        flight, static = (weather.Weather().wind_text(weather.Weather().current_weather())[1] and weather.Weather().wind_text(weather.Weather().current_weather())[1] and (currently_active['closure'] != []) and (currently_active['tfr'] != [])), (currently_active['closure'] != [])
        if Status()._last_active_status['flight'] != flight and Status()._last_active_status['static'] != static:
            if currently_active['closure'] != [] and currently_active['tfr'] != []:
                if not weather.Weather().weather_text(weather.Weather().current_weather())[1]:
                    return '\n<u>Flight is not possible due to weather!</u>🚀❌\nStatic fire or wdr are still possible<i>\nWeather: '+weather.Weather().weather_text(weather.Weather().current_weather())[0]+'</i>'
                elif not weather.Weather().wind_text(weather.Weather().current_weather())[1]:
                    return '\n<u>Flight is not possible due to wind!</u>🚀❌\nStatic fire or wdr are still possible<i>\nWind: '+weather.Weather().wind_text(weather.Weather().current_weather())[0]+'</i>'
                elif not weather.Weather().wind_text(weather.Weather().current_weather())[1] and not weather.Weather().weather_text(weather.Weather().current_weather())[1]:
                    return '\n<u>Flight is not possible due to weather and wind!</u>🚀❌\nStatic fire or wdr are still possible<i>\nWeather: '+weather.Weather().weather_text(weather.Weather().current_weather())[0]+'\nWind: '+weather.Weather().wind_text(weather.Weather().current_weather())[0]+'</i>'
                else:
                    return '\n<u><b>Flight is now possible</b></u>🚀✅'
            elif currently_active['closure'] != [] and currently_active['tfr'] == []:
                if Status()._last_active_status['flight'] != []:
                    return '\n<u>Flight is no longer possible!</u>🚀❌\nStatic fire or wdr are still possible!'
                return '\n<u>Static fire or wdr are now possible!</u>'
            else:
                return '\n<u>Nothing is currently possible!❌</u>'
        Status()._last_active_status['flight'], Status()._last_active_status['static'] = flight, static
        return ''