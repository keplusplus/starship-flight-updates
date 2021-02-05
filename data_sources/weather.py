#https://openweathermap.org/api/
#https://openweathermap.org/weather-conditions#Weather-Condition-Codes-2
#25.997083229714256, -97.15597286864448
#http://history.openweathermap.org/data/2.5/history/city?lat={lat}&lon={lon}&type=hour&start={start}&end={end}&appid={API key}

import requests, json
APIKEY = 'a973723427ca8acbc74e7c47075db6fa'

def today_forecast():
    r = requests.get('http://api.openweathermap.org/data/2.5/onecall',{'lat':25.997083229714256,'lon':-97.15597286864448,'exclude':'current,minutely,hourly,alerts','units':'metric','appid':APIKEY}).json()['daily'][0]
    return {'temp':r['temp']['day'],'feels_like':r['feels_like']['day'],'pressure':r['pressure'],'humidity':r['humidity'],'wind_speed':round(r['wind_speed']*3.6,2),'wind_deg':r['wind_deg'],'weather':r['weather']}


def current_weather():
    r = requests.get('http://api.openweathermap.org/data/2.5/onecall',{'lat':25.997083229714256,'lon':-97.15597286864448,'exclude':'daily,minutely,hourly,alerts','units':'metric','appid':APIKEY}).json()['current']
    return {'temp':r['temp'],'feels_like':r['feels_like'],'pressure':r['pressure'],'humidity':r['humidity'],'wind_speed':round(r['wind_speed']*3.6,2),'wind_deg':r['wind_deg'],'weather':r['weather']}

def wind_text(w:dict, wind_limit = 32):
    wind_speed = w['wind_speed']
    if wind_speed > wind_limit:  #windspeed > 20mph
        return ('Too windy', False)
    elif wind_speed > wind_limit/2:
        return ('Windy', True)
    elif wind_speed > 0:
        return ('Low wind', True)
    else:
        return ('No wind', True)

def wind(wind_speed, wind_limit = 32) -> bool:
    if wind_speed > wind_limit:  #windspeed > 20mph
        return False
    else:
        return True

def weather_text(w:dict):
    weather_id = str(w['weather'][0]['id'])[0]
    out = w['weather'][0]['main']+' ('+w['weather'][0]['description']+')'
    if weather_id in ['8']:    #more id's can be added later
        return (out, True)
    else:
        return (out, False)

def weather(weather_id) -> bool:
    if str(weather_id)[0] in ['8']:    #more id's can be added later
        return True
    else:
        return False
    
