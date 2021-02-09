import requests, time, datetime
bot_token = '1560624792:AAHh0VtVpem5bQ-fK_JDF3e83_Mb7O7yLKQ'    #https://api.telegram.org/botXXX/getUpdates

def send_err_message(message, chatid = 578452596):
    return requests.post('https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + str(chatid) + '&parse_mode=HTML',{'text':'⚠️'+message}).json()

def send_message(chatid, message, disable_link_preview = False):
    #print('<'+message)
    resp =  requests.post('https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + str(chatid) + '&parse_mode=HTML',{'text':message,'disable_web_page_preview':disable_link_preview}).json()
    if not resp['ok']:
        print(resp)
        send_err_message(resp+' message:'+message)
    return resp

def send_photo(chatid, img, caption=''):
    #print('<'+caption+' : '+img)
    if len(caption) > 1024:
        resp = send_photo(chatid,img)
        return (send_message(chatid, caption), resp)
    resp = ''
    if 'http' in img:
        resp = requests.post('https://api.telegram.org/bot'+ bot_token + '/sendPhoto?chat_id='+str(chatid)+ '&parse_mode=HTML',{'photo':img,'caption':caption}).json()
    else:
        resp = requests.post('https://api.telegram.org/bot'+ bot_token + '/sendPhoto?chat_id='+str(chatid)+ '&parse_mode=HTML', files={'photo': open(img, 'rb')}).json()
    if not resp['ok']:
        print(resp)
        send_err_message(resp+' caption:'+caption)
    return resp

def send_channel_message(message, disable_link_preview = False):
    return send_message(-1001163862279, message, disable_link_preview)

def send_channel_photo(img, caption=''):
    return send_photo(-1001163862279, img, caption)
