import telebot, discord

def send_message(message, disable_link_preview = True, color = 7707321):
    telebot.send_channel_message(message,disable_link_preview)
    discord.send_discord_message(message,disable_link_preview, color)

def send_test_message(message, disable_link_preview = True):
    telebot.send_message(telebot.err_channel_id,message,disable_link_preview)

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