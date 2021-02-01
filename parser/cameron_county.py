from bs4 import BeautifulSoup
import requests
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

    def parse(self):
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

            date = datetime.strptime(date_text[date_text.find(', ') + 2:], '%B %d, %Y')
            begin = datetime.combine(date, datetime.strptime(time_text[:time_text.find(' to ')], '%I:%M %p').time())
            end = datetime.combine(date, datetime.strptime(time_text[time_text.find(' to ') + 4:], '%I:%M %p').time())
            
            if 'Canceled' in status_text:
                valid = False
            else:
                valid = True

            self.closures.append({
                'begin': begin,
                'end': end,
                'valid': valid
            })

        return self.closures
