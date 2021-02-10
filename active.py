import database, time, telebot, datetime
from data_sources.weather import Weather
from data_sources import twitter 
from threading import Thread
from status import Status

currently_active = {'closure':[],'tfr':[]}

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

def twitter_filter(text:str) -> bool:
    params = ['flight test']
    for p in params:
        if p in text:
            return True
    return False

def manage_twitter(twit):
    resp = twit.update()
    for x in resp:
        for tweet in resp[x]:
            print(tweet)
            link = 'https://twitter.com/'+x+'/status/'+str(tweet['id'])
            if x in ['elonmusk','SpaceX']:    #usernames where filter is needed
                if twitter_filter(tweet['text']):
                    telebot.send_channel_message('<a href="'+link+'">‌‌<u><b>Tweet by '+twitter.Twitter().names[x]+'</b></u></a>')
            else:
                telebot.send_channel_message('<a href="'+link+'">‌‌<u><b>Tweet by '+twitter.Twitter().names[x]+'</b></u></a>')

def manage_youtube():
    pass    #TODO

def main():
    print('>starting active-main loop')
    twit = twitter.Twitter(120)
    twit.add_twitter_account('elonmusk')
    twit.add_twitter_account('BocaChicaGal')
    twit.add_twitter_account('SpaceX')
    while 1:
        if (currently_active['closure']!=[] and currently_active['tfr']!=[]):
            Weather().weather_change(currently_active=currently_active)
            manage_youtube()
            manage_twitter(twit)
        manage_closures()
        manage_tfrs()
        time.sleep(20)

def start():
    Thread(target=main).start()
    pass