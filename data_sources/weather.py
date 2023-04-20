#https://openweathermap.org/api/
#https://openweathermap.org/weather-conditions#Weather-Condition-Codes-2
#25.997083229714256, -97.15597286864448
#http://history.openweathermap.org/data/2.5/history/city?lat={lat}&lon={lon}&type=hour&start={start}&end={end}&appid={API key}
import requests, json, datetime, telebot, message
import status
from data_sources import dotenv_parser

class Weather:
    APIKEY = dotenv_parser.get_value('.env','WEATHER_KEY')
    _last_current_weather = {'time':datetime.datetime.min,'data':{}}

    def __init__(self):
        pass

    def current_weather(self, sincelastmins = 20):
        try:
            if self._last_current_weather['time'] < datetime.datetime.utcnow()-datetime.timedelta(minutes=sincelastmins):
                r = requests.get('http://api.openweathermap.org/data/2.5/onecall',{'lat':25.997083229714256,'lon':-97.15597286864448,'exclude':'daily,minutely,hourly,alerts','units':'metric','appid':self.APIKEY}).json()['current']
                self._last_current_weather['time'] = datetime.datetime.utcnow()
                self._last_current_weather['data'] = {'temp':r['temp'],'feels_like':r['feels_like'],'pressure':r['pressure'],'humidity':r['humidity'],'wind_speed':round(r['wind_speed']*3.6,2),'wind_deg':r['wind_deg'],'weather':r['weather'][0]}
            return self._last_current_weather['data']
        except Exception as e:
            if e is not requests.ConnectionError:
                message.ErrMessage().sendErrMessage('Error Weather-current-weather!\n\nException:\n' + str(e))
            return {}

    def wind_text(self,w:dict, wind_limit = 30):
        wind_speed = w['wind_speed']
        if wind_speed > wind_limit:  #windspeed > 20mph
            return ('Too windy ('+str(w['wind_speed'])+' km/h, max:'+str(wind_limit)+' km/h)', False)
        elif wind_speed > wind_limit/2:
            return ('Windy ('+str(w['wind_speed'])+' km/h)', True)
        elif wind_speed > 0:
            return ('Low wind ('+str(w['wind_speed'])+' km/h)', True)
        else:
            return ('No wind ('+str(w['wind_speed'])+' km/h)', True)

    def weather_text(self,w:dict):
        weather_id = str(w['weather']['id'])[0]
        out = w['weather']['main']+' ('+w['weather']['description']+')'
        if weather_id in ['8']:    #more id's can be added later
            return (out, True)
        else:
            return (out, False)

    def weather_change(self, w = None, currently_active = None):
        #try:
        if self._last_current_weather['data'] == {}:
            if self.current_weather() == {}:
                return
        last = self._last_current_weather['data']
        if w is None: w = self.current_weather()
        status_message = status.Status().active_change(currently_active)
        if self.weather_text(w)[1] != self.weather_text(last)[1]:
            if self.weather_text(w)[1]:
                message.send_message('<a href="https://openweathermap.org/city/4720060"><b>Weather has changed:</b></a>\n<i>'+self.weather_text(w)[0]+'</i>'+status_message)
            else:
                message.send_message('<a href="https://openweathermap.org/city/4720060"><b>Weather has changed:</b></a>\n<i>'+self.weather_text(w)[0]+'</i>'+status_message)
        elif self.wind_text(w)[1] != self.wind_text(last)[1]:
            if self.wind_text(w)[1]:
                message.send_message('<a href="https://openweathermap.org/city/4720060"><b>Wind has changed:</b></a>\n<i>'+self.wind_text(w)[0]+'</i>'+status_message)
            else:
                message.send_message('<a href="https://openweathermap.org/city/4720060"><b>Wind has changed:</b></a>\n<i>'+self.wind_text(w)[0]+'</i>'+status_message)
        elif self.weather_text(w)[1] != self.weather_text(last)[1] and self.wind_text(w)[1] != self.wind_text(last)[1]:
            out = '<a href="https://openweathermap.org/city/4720060"><b>Weather and wind have changed:</b></a><i>\nWeather: '
            out+= ('✅' if self.weather_text(w)[1]  else '❌')
            out+= ' '+self.weather_text(w)[0]+'\nWind: '
            out+= ('✅' if self.wind_text(w)[1]  else '❌')
            out+= ' '+self.wind_text(w)[0]+'</i>'
            message.send_message(out+status_message)
        #except Exception as e:
        #    message.ErrMessage().sendErrMessage('Error Weather-weather-change!\n\nException:\n' + str(e))
