#https://openweathermap.org/api/
#https://openweathermap.org/weather-conditions#Weather-Condition-Codes-2
#25.997083229714256, -97.15597286864448
#http://history.openweathermap.org/data/2.5/history/city?lat={lat}&lon={lon}&type=hour&start={start}&end={end}&appid={API key}
import requests, json, datetime, telebot
from status import Status

class Weather:
    APIKEY = 'a973723427ca8acbc74e7c47075db6fa'
    _last_current_weather = {'time':datetime.datetime.min,'data':{}}

    def __init__(self):
        pass

    def today_forecast(self):
        try:
            r = requests.get('http://api.openweathermap.org/data/2.5/onecall',{'lat':25.997083229714256,'lon':-97.15597286864448,'exclude':'current,minutely,hourly,alerts','units':'metric','appid':Weather.APIKEY}).json()['daily'][0]
            return {'temp':r['temp']['day'],'feels_like':r['feels_like']['day'],'pressure':r['pressure'],'humidity':r['humidity'],'wind_speed':round(r['wind_speed']*3.6,2),'wind_deg':r['wind_deg'],'weather':r['weather'][0]}
        except Exception as e:
           telebot.send_err_message('Error Weather-today-forecast!\n\nException:\n' + str(e))
           return {}

    def current_weather(self, sincelastmins = 20):
        try:
            if self._last_current_weather['time'] < datetime.datetime.now()-datetime.timedelta(minutes=sincelastmins):
                r = requests.get('http://api.openweathermap.org/data/2.5/onecall',{'lat':25.997083229714256,'lon':-97.15597286864448,'exclude':'daily,minutely,hourly,alerts','units':'metric','appid':self.APIKEY}).json()['current']
                self._last_current_weather['time'] = datetime.datetime.now()
                self._last_current_weather['data'] = {'temp':r['temp'],'feels_like':r['feels_like'],'pressure':r['pressure'],'humidity':r['humidity'],'wind_speed':round(r['wind_speed']*3.6,2),'wind_deg':r['wind_deg'],'weather':r['weather'][0]}
            return self._last_current_weather['data']
        except Exception as e:
            telebot.send_err_message('Error Weather-current-weather!\n\nException:\n' + str(e))
            return {}

    def wind_text(self,w:dict, wind_limit = 32):
        wind_speed = w['wind_speed']
        if wind_speed > wind_limit:  #windspeed > 20mph
            return ('Too windy ('+str(w['wind_speed'])+' km/h, max:30km/h)', False)
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
        try:
            if self._last_current_weather['data'] == {}: self.current_weather()
            last = self._last_current_weather['data']
            if w is None: w = self.current_weather()
            if self.weather_text(w)[1] != self.weather_text(last)[1]:
                if self.weather_text(w)[1]:
                    telebot.send_channel_message('<b>Weather has changed:</b>\n<i>'+self.weather_text(w)[0]+'</i>'+Status().active_change(currently_active))
                else:
                    telebot.send_channel_message('<b>Weather has changed:</b>\n<i>'+self.weather_text(w)[0]+'</i>'+Status().active_change(currently_active))
            elif self.wind_text(w)[1] != self.wind_text(last)[1]:
                if self.wind_text(w)[1]:
                    telebot.send_channel_message('<b>Wind has changed:</b>\n<i>'+self.wind_text(w)[0]+'</i>'+Status().active_change(currently_active))
                else:
                    telebot.send_channel_message('<b>Wind has changed:</b>\n<i>'+self.wind_text(w)[0]+'</i>'+Status().active_change(currently_active))
            elif self.weather_text(w)[1] != self.weather_text(last)[1] and self.wind_text(w)[1] != self.wind_text(last)[1]:
                out = '<b>Weather and wind have changed:</b><i>\nWeather: '
                out+= ('✅' if self.weather_text(w)[1]  else '❌')
                out+= ' '+self.weather_text(w)[0]+'\nWind: '
                out+= ('✅' if self.wind_text(w)[1]  else '❌')
                out+= ' '+self.wind_text(w)[0]+'</i>'
                telebot.send_channel_message(out+Status().active_change(currently_active))
        except Exception as e:
            telebot.send_err_message('Error Weather-weather-change!\n\nException:\n' + str(e))
