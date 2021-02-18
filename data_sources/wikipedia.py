from data_sources import library_helper
library_helper.assure_ext_library('BeautifulSoup4')
from bs4 import BeautifulSoup
import requests
import locale
import telebot
from datetime import datetime, time

class WikipediaParser:
    url = 'https://en.wikipedia.org/wiki/Starship_development_history'
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    
    def __init__(self):
        self.starships = []
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except:
            pass


    def __get_date_by_data_sort_value(self, table_data):
        try:
            date_string = table_data['data-sort-value']
            if len(date_string) == 7:
                date = datetime.strptime(date_string, '%Y-%m')
            elif len(date_string) == 8:
                date = datetime.strptime(date_string, '%Y-%mc')
            elif len(date_string) == 10:
                date = datetime.strptime(date_string, '%Y-%m-%d')
            else:
                return None

            return date.strftime('%b %d %Y')
        except:
            return None
    
    def __fix_string(self, string):
        if type(string) == str:
            string = string.strip()

            if string[-1] == ']':
                string = string[:string.rfind('[')]

        return string

    def parse(self):
        try:
            self.starships = []
            req = requests.get(WikipediaParser.url, WikipediaParser.headers)
            soup = BeautifulSoup(req.content, 'html.parser')
            table = soup.find_all('table')[4].find('tbody')
            rows = table.find_all('tr')
            del rows[0]
            for row in rows:
                starship = {}
                data = row.find_all('td')
                starship['name'] = data[0].get_text()
                starship['firstSpotted'] = data[1].get_text() if self.__get_date_by_data_sort_value(data[1]) == None else self.__get_date_by_data_sort_value(data[1])
                starship['rolledOut'] = data[2].get_text() if self.__get_date_by_data_sort_value(data[2]) == None else self.__get_date_by_data_sort_value(data[2])
                starship['firstStaticFire'] = data[3].get_text() if self.__get_date_by_data_sort_value(data[3]) == None else self.__get_date_by_data_sort_value(data[3])
                starship['maidenFlight'] = data[4].get_text() if self.__get_date_by_data_sort_value(data[4]) == None else self.__get_date_by_data_sort_value(data[4])
                starship['decomissioned'] = data[5].get_text() if self.__get_date_by_data_sort_value(data[5]) == None else self.__get_date_by_data_sort_value(data[5])
                starship['constructionSite'] = data[6].get_text()
                starship['status'] = data[7].get_text()
                starship['flights'] = int(data[8].get_text())
                
                for key in starship:
                    starship[key] = self.__fix_string(starship[key])

                self.starships.append(starship)
            
            return self.starships
        except Exception as e:
            telebot.send_err_message('Error parsing Starship development history (Wikipedia)!\n\nException:\n' + str(e))
            return []
