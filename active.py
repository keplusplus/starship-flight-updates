import database, time, telebot, datetime
from data_sources.weather import Weather
from data_sources.twitter import Twitter
from threading import Thread
from status import Status

currently_active = {'closure':[],'tfr':[]}
twitter = None

def manage_closures(inlastmin = 20):
    if database.road_closure_active() != []:
        for x in database.road_closure_active():
            if x not in currently_active['closure']:
                currently_active['closure'].append(x)
                if x[0]+datetime.timedelta(minutes=inlastmin) > datetime.datetime.now()-datetime.timedelta(hours=1):
                    telebot.send_channel_message('<b>Road closure now active!</b>\n(<i>From '+database.datetime_to_string(x[0])+' to '+database.datetime_to_string(x[1])+' UTC</i>)'+Status().active_change(currently_active))
    for x in currently_active['closure']:
        if x not in database.road_closure_active():
            currently_active['closure'].remove(x)
            telebot.send_channel_message('<b>Road closure no longer active!</b>\n(<i><s>From '+database.datetime_to_string(x[0])+' to '+database.datetime_to_string(x[1])+' </s>UTC</i>)'+Status().active_change(currently_active))

def manage_tfrs(inlastmin = 20):
    if database.faa_active() != []:
        for x in database.faa_active():
            if x not in currently_active['tfr']:
                currently_active['tfr'].append(x)
                if x[0]+datetime.timedelta(minutes=inlastmin) > datetime.datetime.now()-datetime.timedelta(hours=1):
                    telebot.send_channel_message('<b>TFR (unlimited) now active!</b>\n(<i>From '+database.datetime_to_string(x[0])+' to '+database.datetime_to_string(x[1])+' UTC</i>)'+Status().active_change(currently_active))
    for x in currently_active['tfr']:
        if x not in database.faa_active():
            currently_active['tfr'].remove(x)
            telebot.send_channel_message('<b>TFR (unlimited) no longer active!</b>\n(<i><s>From '+database.datetime_to_string(x[0])+' to '+database.datetime_to_string(x[1])+'</s> UTC</i>)'+Status().active_change(currently_active))

def main(): #this should tell when closure/tfr is now or no longer active
    #twitter = Twitter(1440)
    #print(twitter.add_twitter_account('s_fliens'))
    while True:
        print(currently_active)
        if (currently_active['closure']!=[] and currently_active['tfr']!=[]):
            Weather().weather_change(currently_active=currently_active)
            print('should listen on apis')
        manage_closures()
        manage_tfrs()
        #print(twitter.update())
        time.sleep(20)

def start():
    Thread(target=main).start()
    pass