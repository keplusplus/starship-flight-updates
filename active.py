import time, datetime, message
from data_sources.weather import Weather
from database import Database, CameronCountyData, FAAData
from data_sources import twitter, youtube
from threading import Thread
from status import Status

currently_active = {'closure':[],'tfr':[]}

def manage_closures(inlastmin = 1):
    if CameronCountyData().road_closure_active() != []:
        for x in CameronCountyData().road_closure_active():
            if x not in currently_active['closure']:
                currently_active['closure'].append(x)
                if x[0]+datetime.timedelta(minutes=inlastmin) > datetime.datetime.utcnow():
                    message.send_message('<a href="https://www.cameroncounty.us/spacex/"><b>Road closure now active!</b></a>\n(<i>From '+Database().datetime_to_string(x[0])+' to '+Database().datetime_to_string(x[1])+' UTC</i>)'+Status().active_change(currently_active))
    for x in currently_active['closure']:
        if x not in CameronCountyData().road_closure_active():
            currently_active['closure'].remove(x)
            message.send_message('<a href="https://www.cameroncounty.us/spacex/"><b>Road closure no longer active!</b></a>\n(<i><s>From '+Database().datetime_to_string(x[0])+' to '+Database().datetime_to_string(x[1])+' </s>UTC</i>)'+Status().active_change(currently_active))

def manage_tfrs(inlastmin = 1):
    if FAAData().faa_active() != []:
        for x in FAAData().faa_active():
            if x not in currently_active['tfr']:
                currently_active['tfr'].append(x)
                if x[0]+datetime.timedelta(minutes=inlastmin) > datetime.datetime.utcnow():
                    message.send_message('<a href="https://tfr.faa.gov/tfr_map_ims/html/cc/scale7/tile_33_61.html"><b>TFR (unlimited) now active!</b></a>\n(<i>From '+Database().datetime_to_string(x[0])+' to '+Database().datetime_to_string(x[1])+' UTC</i>)'+Status().active_change(currently_active))
    for x in currently_active['tfr']:
        if x not in FAAData().faa_active():
            currently_active['tfr'].remove(x)
            message.send_message('<a href="https://tfr.faa.gov/tfr_map_ims/html/cc/scale7/tile_33_61.html"><b>TFR (unlimited) no longer active!</b></a>\n(<i><s>From '+Database().datetime_to_string(x[0])+' to '+Database().datetime_to_string(x[1])+'</s> UTC</i>)'+Status().active_change(currently_active))

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
            'evac'
        ]
    }
    params = f[user]
    for p in params:
        if p.lower() in text.lower():
            return True
    return False

def handle_elon(twit:twitter.Twitter):
    if twit.get_Name('elonmusk') is None and currently_active['closure']!=[] and currently_active['tfr']!=[]:
        #logger.debug('add elon')
        twit.add_twitter_account('elonmusk')
    elif twit.get_Name('elonmusk') is not None and not (currently_active['closure']!=[] and currently_active['tfr']!=[]):
        print('remove elon')
        twit.remove_twitter_account('elonmusk')

def manage_twitter(twit:twitter.Twitter):
    handle_elon(twit)
    resp = twit.update()
    if resp is None:
        return
    for x in resp:
        for tweet in resp[x]:
            link = 'https://twitter.com/'+x+'/status/'+str(tweet['id'])
            if twitter_filter(x, tweet['text']):
                message.send_message('<a href="'+link+'">‌‌<b>Tweet by '+twit.get_Name(x)+'</b>\n(@'+x+' on Twitter)</a>',False)

def manage_youtube(yt:youtube.Youtube()):
    update = yt.update()
    if update is not None:
        for x in update:
            message.send_message('<a href="'+x+'">‌‌<u><b>New Video by SpaceX</b></u></a>',False)

def main(twit:twitter.Twitter, logger, cycle_seconds = 20):
    logger.debug('>starting active-main loop')
    yt = youtube.Youtube()
    while 1:
        manage_closures()
        manage_tfrs()
        if (currently_active['closure']!=[] and currently_active['tfr']!=[]):
            Weather().weather_change(currently_active=currently_active)
            manage_youtube(yt)
        elif CameronCountyData().road_closure_today()[0] and FAAData().faa_today()[0] and datetime.datetime.utcnow().time() > Database().daily_message_time:
            Weather().weather_change()
        if currently_active['closure']!=[] or currently_active['tfr']!=[]:
            manage_twitter(twit)
        time.sleep(cycle_seconds)

def start(twit:twitter.Twitter, logger):
    Thread(target=main, args=(twit,logger)).start()
    pass