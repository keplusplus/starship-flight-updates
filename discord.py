from typing import Text
import requests
from data_sources import dotenv_parser

url = dotenv_parser.get_value('.env','DISCORD_URL')

def handle_link(text:str , disable_link_preview:bool):  #rekursive
    if '<a' not in text:
        return text
    beforelink = text.split('<a',1)[0]
    afterlink = text.split('</a>',1)[-1]
    unformatted = text.split('<a',1)[1].split('</a>',1)[0]
    link = ''
    if "'" in unformatted:
        link = unformatted.split("'")[1]
    else:
        link = unformatted.split('"')[1]
    linktext = unformatted.split('>',1)[-1]
    preview = ''
    if not disable_link_preview:
        preview = '\n'+link
    else:
        link = '<'+link+'>'
    return handle_link(beforelink+'['+linktext+']('+link+')'+afterlink+preview,disable_link_preview)

def send_discord_message(text:str, disable_link_preview = False, color = 7707321):
    text = text.replace('<b>','**').replace('</b>','**')    #bold
    text = text.replace('<u>','__').replace('</u>','__')    #underline
    text = text.replace('<i>','_').replace('</i>','_')      #italic
    text = text.replace('<s>','~~').replace('</s>','~~')    #strike
    text = handle_link(text,disable_link_preview)
    if disable_link_preview:
        requests.post(url, json = {'embeds':[{'description':text,'color': color},]}) #embed
    else:
        requests.post(url, json = {'content':text})