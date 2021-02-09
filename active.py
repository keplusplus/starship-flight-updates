import database, time, telebot, datetime
from data_sources.weather import Weather
from threading import Thread

currently_active = {'closure':[],'tfr':[]}

def status() -> str:    #TODO weather is missing!
    if currently_active['closure'] != []:
        return '\n<i>Static fire or wdr are still possible</i>'
    elif currently_active['closure'] != [] and currently_active['tfr'] != []:
        return '\n<u><b>Flight is now possible</b></u>🚀✅'
    elif currently_active['closure'] == [] and currently_active['tfr'] == []:
        return '\n<i>Nothing is possible anymore</i>'
    return ''

def manage_closures():
    if database.road_closure_active() != []:
        for x in database.road_closure_active():
            if x not in currently_active['closure']:
                currently_active['closure'].append(x)
                if x[0]+datetime.timedelta(minutes=30) > datetime.datetime.now()-datetime.timedelta(hours=1):
                    telebot.send_channel_message('Road closure now active❕\n<i>(From '+database.datetime_to_string(x[0])+' to '+database.datetime_to_string(x[1])+' UTC)</i>'+status())
    for x in currently_active['closure']:
        if x not in database.road_closure_active():
            currently_active['closure'].remove(x)
            telebot.send_channel_message('Road closure no longer active❗\n<i><s>(From '+database.datetime_to_string(x[0])+' to '+database.datetime_to_string(x[1])+' UTC)</s></i>'+status())

def manage_tfrs():
    if database.faa_active() != []:
        for x in database.faa_active():
            if x not in currently_active['tfr']:
                currently_active['tfr'].append(x)
                if x[0]+datetime.timedelta(minutes=30) > datetime.datetime.now()-datetime.timedelta(hours=1):
                    telebot.send_channel_message('TFR (unlimited) now active❕\n<i>(From '+database.datetime_to_string(x[0])+' to '+database.datetime_to_string(x[1])+' UTC)</i>'+status())
    for x in currently_active['tfr']:
        if x not in database.faa_active():
            currently_active['tfr'].remove(x)
            telebot.send_channel_message('TFR (unlimited) no longer active❗\n<i><s>(From '+database.datetime_to_string(x[0])+' to '+database.datetime_to_string(x[1])+' UTC)</s></i>'+status())

def main(): #this should tell when closure/tfr is now or no longer active
    while True:
        if (currently_active['closure']!=[] and currently_active['tfr']!=[]):
            Weather().weather_change()
            print('should listen on apis')
        manage_closures()
        manage_tfrs()   
        time.sleep(20)

def start():
    Thread(target=main).start()
    pass