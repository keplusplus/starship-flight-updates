from data_sources import weather
import database

class Status:

    _last_status = {'flight':None,'static':None}
    _last_active_status = {'flight':None,'static':None}

    def __init__(self):
        pass

    def daily_status(self, w) -> str:  #called by min-daily
        out = ''
        flight = (weather.Weather().weather_text(w)[1] and weather.Weather().wind_text(w)[1] and bool(database.road_closure_today()[0]) and database.faa_today()[0])
        staticfire = bool(database.road_closure_today()[0])
        if flight:
            out+='\n<u><b>Flight is possible today</b></u>🚀✅\n'
        else:
            out+='\n<u><b>Presumably no flight today</b></u>🚀❌\n'
        if staticfire:
            out+='Static fire or wdr are still possible\n'
        else:
            out+='Nothing big happening on current data❗\n'
        return out

    def value_change_status(self, conn = None) -> str:   #called when new/change/remove closure/tfr
        return ''
        flight = weather.Weather().weather_text(weather.Weather().current_weather.Weather())[1] and weather.Weather().wind_text(weather.Weather().current_weather.Weather())[1] and database.road_closure_today(conn)[0] and database.faa_today(conn)[0]
        static = database.road_closure_today(conn)[0]
        out = ''
        if Status()._last_status['flight'] is not None:
            if Status()._last_status['flight'] != flight:
                if flight:
                    out = '\n<u><b>Flight is now possible today</b></u>❕\n'
                else:
                    out = '\n<u><b>Flight is no longer possible today</b></u>❗\n'
            if Status()._last_status['static'] != static:
                if static:
                    out+= '<i>Static fire or wdr are now possible today</i>❕'
                else:
                    return '<i>Nothing is possible anymore today</i>❗'
            if Status()._last_status['flight'] == flight and Status()._last_status['static'] == static:
                out = '\n[no status change, flight: '+str(flight)+'|staticfire: '+str(static)+']'
        Status()._last_status['flight'], Status()._last_status['static'] = flight, static
        return out
    
    def active_change(self, currently_active) -> str:
        flight, static = (weather.Weather().wind_text(weather.Weather().current_weather.Weather())[1] and weather.Weather().wind_text(weather.Weather().current_weather.Weather())[1] and (currently_active['closure'] != []) and (currently_active['tfr'] != [])), (currently_active['closure'] != [])
        if Status()._last_active_status['flight'] != flight and Status()._last_active_status['static'] != static:
            if currently_active['closure'] != [] and currently_active['tfr'] != []:
                if not weather.Weather().weather_text(weather.Weather().current_weather.Weather())[1]:
                    return '\n<u>Flight is not possible due to weather!</u>❌<i>\n(Weather: '+weather.Weather().weather_text(weather.Weather().current_weather.Weather())[0]+')</i>'
                elif not weather.Weather().wind_text(weather.Weather().current_weather.Weather())[1]:
                    return '\n<u>Flight is not possible due to wind!</u>❌<i>\n(Wind: '+weather.Weather().wind_text(weather.Weather().current_weather.Weather())[0]+')</i>'
                elif not weather.Weather().wind_text(weather.Weather().current_weather.Weather())[1] and not weather.Weather().weather_text(weather.Weather().current_weather.Weather())[1]:
                    return '\n<u>Flight is not possible due to weather and wind!</u>❌<i>\n(Weather: '+weather.Weather().weather_text(weather.Weather().current_weather.Weather())[0]+')\n(Wind: '+weather.Weather().wind_text(weather.Weather().current_weather.Weather())[0]+')</i>'
                else:
                    return '\n<u><b>Flight is now possible</b></u>🚀✅'
            elif currently_active['closure'] != [] and currently_active['tfr'] == []:
                return '\n<u>Static fire or wdr are now possible!</u>'
            else:
                return '\n<u>Nothing is currently possible!❌</u>'
        Status()._last_active_status['flight'], Status()._last_active_status['static'] = flight, static
        return ''