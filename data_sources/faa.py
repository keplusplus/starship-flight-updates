from bs4 import BeautifulSoup
import requests
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
        
        rows = table.find_all('tr')
        for row in rows:
            print(row)
