import requests, time, datetime
bot_token = '1560624792:AAHh0VtVpem5bQ-fK_JDF3e83_Mb7O7yLKQ'    #https://api.telegram.org/botXXX/getUpdates

def send_message(chatid, message):
    #print('<'+message)
    return requests.post('https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + str(chatid) + '&parse_mode=MarkdownV2',{'text':message}).json()

def send_photo(chatid, img, caption=''):
    #print('<'+caption+' : '+img)
    if len(caption) > 1024:
        resp = send_photo(chatid,img)
        return (send_message(chatid, caption), resp)
    if 'http' in img:
        return requests.post('https://api.telegram.org/bot'+ bot_token + '/sendPhoto?chat_id='+str(chatid)+ '&parse_mode=MarkdownV2',{'photo':img,'caption':caption}).json()
    else:
        return requests.post('https://api.telegram.org/bot'+ bot_token + '/sendPhoto?chat_id='+str(chatid)+ '&parse_mode=MarkdownV2', files={'photo': open(img, 'rb')}).json()

def send_err_message(message):
    return send_message('⚠️'+message)

def send_channel_message(message):
    return send_message(-1001163862279, message)

def send_channel_photo(img, caption=''):
    return send_photo(-1001163862279, img, caption)
