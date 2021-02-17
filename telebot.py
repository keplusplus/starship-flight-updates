import requests, time, datetime
from data_sources import dotenv_parser
bot_token = dotenv_parser.get_value('.env','TELEBOT_TOKEN')    #https://api.telegram.org/botXXX/getUpdates
channel_id = dotenv_parser.get_value('.env','TELEBOT_CHANNEL')

def send_err_message(message, chatid = -558082586):
    try:
        return requests.post('https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + str(chatid) ,{'text':'⚠️'+message,'disable_web_page_preview':True}).json()
    except: pass

def send_message(chatid, message, disable_link_preview = False):
    #print('<'+message)
    resp = ''
    try:
        resp =  requests.post('https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + str(chatid) + '&parse_mode=HTML',{'text':message,'disable_web_page_preview':disable_link_preview}).json()
    except: pass
    if not resp['ok']:
        print(resp)
        send_err_message(str(resp)+'\n\nmessage:'+message)
    return resp

def send_photo(chatid, img, caption=''):
    #print('<'+caption+' : '+img)
    if len(caption) > 1024:
        resp = send_photo(chatid,img)
        return (send_message(chatid, caption), resp)
    resp = ''
    if 'http' in img:
        try:
            resp = requests.post('https://api.telegram.org/bot'+ bot_token + '/sendPhoto?chat_id='+str(chatid)+ '&parse_mode=HTML',{'photo':img,'caption':caption}).json()
        except: pass
    else:
        try:
            resp = requests.post('https://api.telegram.org/bot'+ bot_token + '/sendPhoto?chat_id='+str(chatid)+ '&parse_mode=HTML', files={'photo': open(img, 'rb')}).json()
        except: pass
    if not resp['ok']:
        print(resp)
        send_err_message(str(resp)+'\n\ncaption:'+caption)
    return resp

def send_channel_message(message, disable_link_preview = False):
    return send_message(channel_id, message, disable_link_preview)

def send_channel_photo(img, caption=''):
    return send_photo(channel_id, img, caption)
