from message import ErrMessage
from data_sources import library_helper
library_helper.assure_ext_library('BeautifulSoup4')
from bs4 import BeautifulSoup
library_helper.assure_ext_library('python-dateutil')
import dateutil.parser as dparser
import requests
import locale
import telebot
from datetime import datetime, time

class CameronCountyParser:
    url = 'https://www.cameroncounty.us/spacex/'
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    closures = []

    def __init__(self):
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except: pass

    def parse(self):
        try:
            self.closures = []
            req = requests.get(self.url, self.headers)
            soup = BeautifulSoup(req.content, 'html.parser')
            table = soup.find('table')
            tr = table.find('tbody').find_all('tr')
            for row in tr:
                td = row.find_all('td')
                date_text = td[1].get_text()
                time_text = td[2].get_text()
                status_text = td[3].get_text()

                if '' in [date_text.strip(), time_text.strip(), status_text.strip()]:
                    continue    #skips this iteration if this row has empty values

                begin = dparser.parse(date_text.lower().split('to')[0],fuzzy=True).date()
                end = begin
                if 'to' in date_text.lower():
                    end = dparser.parse(date_text.lower().split('to')[1],fuzzy=True).date()
                
                begin = datetime.combine(begin, dparser.parse(time_text.lower().split('to')[0],fuzzy=True).time())
                end = datetime.combine(begin, dparser.parse(time_text.lower().split('to')[1],fuzzy=True).time())
                
                if 'scheduled' in status_text.lower():
                    valid = True
                else:
                    valid = False

                self.closures.append({
                    'begin': begin,
                    'end': end,
                    'valid': valid
                })
            
            return self.closures
        except Exception as e:
            ErrMessage().sendErrMessage('Error parsing Cameron County Road Closures!\n\nException:\n' + str(e))
            return []
