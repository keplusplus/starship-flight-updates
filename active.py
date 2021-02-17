import database, time, telebot, datetime
from data_sources.weather import Weather
from data_sources import twitter, youtube
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

def twitter_filter(user:str, text:str) -> bool:
    f = {
    'SpaceX':[
        'Starship',
        'flight test'
    ],
    'elonmusk':[
        'Starship',
        'SN'
    ],
    'BocaChicaGal':[
        'Alert',
        'evacuation',
        'notice'
    ]
    }
    params = f[user]
    for p in params:
        if p.lower() in text.lower():
            return True
    return False

def manage_twitter(twit:twitter.Twitter):
    resp = twit.update()
    for x in resp:
        for tweet in resp[x]:
            print(tweet)
            link = 'https://twitter.com/'+x+'/status/'+str(tweet['id'])
            #if x in ['elonmusk','SpaceX']:    #usernames where filter is needed
            if twitter_filter(x, tweet['text']):
                telebot.send_channel_message('<a href="'+link+'">‌‌<u><b>Tweet by '+twit.get_Name(x)+'</b></u></a>')

def manage_youtube(yt:youtube.Youtube()):
    update = yt.update()
    if update is not None:
        for x in update:
            telebot.send_channel_message('<a href="'+x+'">‌‌<u><b>New Video by SpaceX</b></u></a>')

def handle_elon(twit:twitter.Twitter):
    if twit.get_Name('elonmusk') is None and currently_active['closure']!=[] and currently_active['tfr']!=[]:
        twit.add_twitter_account('elonmusk')
    elif twit.get_Name('elonmusk') is not None:
        twit.remove_twitter_account('elonmusk')

def main():
    print('>starting active-main loop')
    yt = youtube.Youtube(20)
    twit = twitter.Twitter(2000)
    twit.add_twitter_account('BocaChicaGal')
    twit.add_twitter_account('SpaceX')
    while 1:
        manage_closures()
        manage_tfrs()
        if (currently_active['closure']!=[] and currently_active['tfr']!=[]):
            Weather().weather_change(currently_active=currently_active)
            manage_youtube(yt)
        handle_elon(twit)
        manage_twitter(twit)
        time.sleep(20)

def start():
    Thread(target=main).start()
    pass