import requests, json, datetime
from data_sources import library_helper, dotenv_parser
library_helper.assure_ext_library('xmltodict')
import xmltodict

#live info#j = requests.get('https://www.googleapis.com/youtube/v3/videos',{'part':'contentDetails,liveStreamingDetails,snippet','id':'32WyWxgwHMo','key':APIKEY}).json()

class Youtube:

    APIKEY = dotenv_parser.get_value('.env','YOUTUBE_KEY')

    def __init__(self, timespan=0):
        self.timespan = timespan
        self.latest_video = {}
        self.channels = ['UCtI0Hodo5o5dUb67FeUjDeA',]

    def _filter(self, text: str) -> bool:
        if 'Flight Test' in text:
            return True
        return False

    def _go_trough_all_videos(self, channel):
        out = []
        last_time = datetime.datetime.now()-datetime.timedelta(minutes=self.timespan)
        if channel in self.latest_video:
            last_time = self.latest_video[channel]
        data = None
        try:
            requests.get('https://www.youtube.com/feeds/videos.xml?',{'channel_id':channel})
        except:
            pass
        if data is None: return None
        for entry in reversed(xmltodict.parse(data.content)['feed']['entry']):
            if datetime.datetime.strptime(entry['published'],"%Y-%m-%dT%H:%M:%S%z").replace(tzinfo=None) > last_time:
                last_time = datetime.datetime.strptime(entry['published'],"%Y-%m-%dT%H:%M:%S%z").replace(tzinfo=None)
                if self._filter(entry['media:group']['media:title']):   #print(json.dumps(entry,indent=2,sort_keys=False))
                    out.append(entry['link']['@href'])
        self.latest_video[channel] = last_time
        return out

    def update(self):
        out = []
        for channel in self.channels:
            resp = self._go_trough_all_videos(channel)
            if resp is None: return None
            out += resp
        return out

