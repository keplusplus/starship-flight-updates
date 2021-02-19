import requests, time, datetime
from data_sources import dotenv_parser
bot_token = dotenv_parser.get_value('.env','TELEBOT_TOKEN')    #https://api.telegram.org/botXXX/getUpdates
channel_id = dotenv_parser.get_value('.env','TELEBOT_CHANNEL')
err_channel_id = dotenv_parser.get_value('.env','TELEBOT_ERR_CHANNEL')

def send_err_message(message, chatid = err_channel_id):
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

def history_message(data:dict, changes:dict = {}) -> str:
    for d in data:  #underline changes
        if d in changes:
            data[d] = '<u>'+str(data[d])+'</u>\n<i>(was '+changes[d][-1]+')</i>'
    out = '<a href="https://en.wikipedia.org/wiki/Starship_development_history"><b>𝗗𝗲𝘃𝗲𝗹𝗼𝗽𝗺𝗲𝗻𝘁 𝗨𝗽𝗱𝗮𝘁𝗲</b></a>\n'
    out+='<u><b>'+data['name']+'</b></u> '
    if changes == {}:
        out+='<b><i>(NEW!)</i></b>'
    out+='\n'
    out+='<b>First Spotted: </b>'
    out+=data['firstSpotted']+'\n'
    out+='<b>Rolled Out: </b>'
    out+=data['rolledOut']+'\n'
    out+='<b>First Static Fire: </b>'
    out+=data['firstStaticFire']+'\n'
    out+='<b>Maiden Flight: </b>'
    out+=data['maidenFlight']+'\n'
    out+='<b>Decomissioned: </b>'
    out+=data['decomissioned']+'\n'
    out+='<b>Construction Site: </b>'
    out+=data['constructionSite']+'\n'
    out+='<b>Status: </b>'
    out+=data['status']+'\n'
    out+='<b>Flights: </b>'
    out+=str(data['flights'])+'\n'
    return out
