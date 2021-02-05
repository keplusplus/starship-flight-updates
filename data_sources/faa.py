from bs4 import BeautifulSoup
import requests
import locale
from datetime import datetime, time

class FAAParser:
    url = 'https://tfr.faa.gov/tfr_map_ims/html/cc/scale7/tile_33_61.html'
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    tfrs = []

    def __init__(self):
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

    def parse(self):
        self.tfrs = []
        req = requests.get(self.url, self.headers)
        soup = BeautifulSoup(req.content, 'html.parser')
        all_tables = soup.find_all('table')
        tables = []
        for table in all_tables:
            try:
                if table['bgcolor'] == 'LightSteelBlue':
                    tables.append(table)
            except KeyError:
                pass
        
        rows = tables[1].find_all('tr')
        space_entries = []
        for row in rows:
            try:
                if 'SPACE OPERATIONS' in row.find_all('td')[4].get_text():
                    space_entries.append(row)
            except IndexError:
                pass
        
        links = []
        for se in space_entries:
            if 'BROWNSVILLE' in se.find_all('td')[5].get_text():
                links.append(se.find_all('td')[5].find('a')['href'])
        
        for url in links:
            req = requests.get(url, self.headers)
            soup = BeautifulSoup(req.content, 'html.parser')
            tables = soup.find_all('table')

            tables500 = []
            for table in tables:
                try:
                    if table['width'] == '500':
                        tables500.append(table)
                except KeyError:
                    pass
            
            if len(tables500) < 2:
                continue
            
            tfr = {}

            for row in tables500[0].find_all('tr'):
                try:
                    if 'Beginning' in row.find_all('td')[0].get_text():
                        begin_text = row.find_all('td')[1].get_text().strip()
                        begin_datetime = datetime.strptime(begin_text, '%B %d, %Y at %H%M UTC')
                        tfr['begin'] = begin_datetime
                    if 'Ending' in row.find_all('td')[0].get_text():
                        end_text = row.find_all('td')[1].get_text().strip()
                        end_datetime = datetime.strptime(end_text, '%B %d, %Y at %H%M UTC')
                        tfr['end'] = end_datetime
                except IndexError:
                    pass
            
            for row in tables500[1].find_all('tr'):
                try:
                    if 'Altitude' in row.find_all('td')[2].get_text():
                        altitude_text = row.find_all('td')[2].get_text()
                        if 'surface' in altitude_text:
                            tfr['fromSurface'] = True
                        else:
                            tfr['fromSurface'] = False
                        
                        to_alt = altitude_text[altitude_text.find('up to and including ') + 20:altitude_text.find(' feet MSL')]
                        tfr['toAltitude'] = int(to_alt)
                except IndexError:
                    pass
            
            try:
                tfr['begin']
                tfr['end']
                tfr['fromSurface']
                tfr['toAltitude']

                self.tfrs.append(tfr)
            except KeyError:
                pass

        return self.tfrs
