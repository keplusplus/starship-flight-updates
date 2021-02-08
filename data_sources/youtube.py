import requests, json
import library_helper
library_helper.assure_ext_library('xmltodict')
import xmltodict
#https://developers.google.com/youtube/v3/docs
#https://developers.google.com/youtube/v3/docs/videos/list
#https://developers.google.com/youtube/v3/docs/videos
#https://developers.google.com/youtube/v3/determine_quota_cost limit is 10000units
APIKEY = 'AIzaSyBVgZV4-_MzfS9oENPjuH8kX11OOv5Clzg'
nsf_id = 'UCSUu1lih2RifWkKtDOJdsBA'
k =  'UCn4sPeUomNGIr26bElVdDYg'

#print(requests.get('https://www.googleapis.com/youtube/v3/channels',{'id':nsf_id,'key':APIKEY}).json())
#live info#j = requests.get('https://www.googleapis.com/youtube/v3/videos',{'part':'contentDetails,liveStreamingDetails,snippet','id':'32WyWxgwHMo','key':APIKEY}).json()
#all videos for channel(max)#j = requests.get('https://www.googleapis.com/youtube/v3/search',{'order':'date','part':'snippet','channelId':'UCSUu1lih2RifWkKtDOJdsBA','maxResluts':25,'key':APIKEY}).json()
#print(json.dumps(j,indent=2,sort_keys=True))
#https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails,id,snippet,status&playlistId=UUSUu1lih2RifWkKtDOJdsBA&key=AIzaSyBVgZV4-_MzfS9oENPjuH8kX11OOv5Clzg&maxResults=20 <- does not list live stuff
#https://www.youtube.com/feeds/videos.xml?channel_id=UCFwMITSkc1Fms6PoJoh1OUQ <- access rss feed of channel
print(json.dumps(xmltodict.parse(requests.get('https://www.youtube.com/feeds/videos.xml?channel_id=UC3AeSXcVWKrJyYSwcexuf3Q').content),indent=2,sort_keys=False))
