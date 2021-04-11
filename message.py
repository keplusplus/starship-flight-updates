import telebot, discord, datetime, status, database, sys, os
from data_sources.weather import Weather

class ErrMessage:
    errMessages = {}    #key = errMessage; value = datetime

    def __init__(self) -> None:
        pass

    def errorInfo(self) -> str:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        return '\n\nType:\n'+str(exc_type)+'\n\nLocation\nFile: '+str(fname)+'\nLine: '+str(exc_tb.tb_lineno)

    def sendErrMessage(self, message, mustPassedHours = 2):
        message += self.errorInfo()
        if ErrMessage.errMessages.get(message, datetime.datetime.min) < datetime.datetime.now() - datetime.timedelta(hours=mustPassedHours):  #if err not in last 2 hours
            try:
                telebot.send_err_message(message)
            except: pass
            try:
                discord.send_discord_error_message(message)
            except: pass
        ErrMessage.errMessages[message] = datetime.datetime.now()

def send_message(message, disable_link_preview = True, color = 7707321):
    if message == '':
        return
    telebot.send_channel_message(message,disable_link_preview)
    discord.send_discord_message(message,disable_link_preview, color)

def send_test_message(message, disable_link_preview = True):
    if message == '':
        return
    telebot.send_message(telebot.err_channel_id,message,disable_link_preview)

def send_raw(text:str):
    pass

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

def daily_update_message(closures, tfrs, weather) -> str:
    db = database.Database()
    
    flight = (Weather().weather_text(weather)[1] and Weather().wind_text(weather)[1] and closures[0] and tfrs[0])
    staticfire = closures[0]
    if datetime.date.today().weekday() > 4 and not flight:
        print('weekend and nothing possible')
        return ''
    flightStr = 'yes' if flight else 'no'
    staticStr = 'yes' if staticfire else 'no'
    #Header & Roadclosure
    out = '<b>𝗗𝗮𝗶𝗹𝘆 𝗙𝗹𝗶𝗴𝗵𝘁 𝗦𝘁𝗮𝘁𝘂𝘀+</b> <i>[flight: '+flightStr+'| static: '+staticStr+']</i>\nCurrent Time UTC: '+db.datetime_to_string(datetime.datetime.utcnow())+' local: '+db.datetime_to_local_string(datetime.datetime.utcnow())+'\n<a href="https://www.cameroncounty.us/spacex/"><b>Road Closure:</b></a>'
    if closures[0]:
        out+= '✅\n'
        for x in closures[1:]:
            out+= 'from '+db.datetime_to_string(x[0])+' to '+db.datetime_to_string(x[1])+' (UTC)'
            out+= '\n<i>(local: '+db.datetime_to_local_string(x[0])+' to '+db.datetime_to_local_string(x[1])+')</i>\n'
    else:
        out+= '❌\nnothing scheduled!\n'
    #TFR
    out+='<a href="https://tfr.faa.gov/tfr_map_ims/html/cc/scale7/tile_33_61.html"><b>TFR:</b></a>'
    if tfrs[0]:
        out+='✅\n'
    else:
        out+='❌\n'
        if len(tfrs) != 1:
            out+='(max alt. needs to be unlimited for flight)\n'
    unlimited, limited = False, False
    for x in tfrs[1:]:
        if x[3]:
            unlimited = True
            out+='from '+db.datetime_to_string(x[0])+' to '+db.datetime_to_string(x[1])+' (max alt.: unlimited)\n'
            out+='<i>(local from '+db.datetime_to_local_string(x[0])+' to '+db.datetime_to_local_string(x[1])+')</i>\n'
        else:
            limited = True
    if unlimited and limited:
        out+='-----\n'
    for x in tfrs[1:]:
        if not x[3]:
            out+='<i>from '+db.datetime_to_string(x[0])+' to '+db.datetime_to_string(x[1])+' (max alt.: '+str(x[2])+' ft)</i>\n'
    #Weather
    out+='<a href="https://openweathermap.org/city/4720060"><b>Weather today:</b></a>'
    if Weather().weather_text(weather)[1]:
        out+='✅\n'+Weather().weather_text(weather)[0]+'\n'
    else:
        out+='❌\n'+Weather().weather_text(weather)[0]+'\n'
    #Wind
    out+='<a href="https://openweathermap.org/city/4720060"><b>Wind:</b></a>'
    if Weather().wind_text(weather)[1]:
        out+='✅\n'+Weather().wind_text(weather)[0]+'\n'
    else:
        out+='❌\n'+Weather().wind_text(weather)[0]+'\n'
    #Flight Message
    out += status.Status().daily_status(weather)
    out+='<i>(We will keep you updated if anything changes!)</i>'
    return out