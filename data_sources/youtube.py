import requests, json
#https://developers.google.com/youtube/v3/docs
#https://developers.google.com/youtube/v3/docs/videos/list
#https://developers.google.com/youtube/v3/docs/videos
APIKEY = 'AIzaSyBVgZV4-_MzfS9oENPjuH8kX11OOv5Clzg'
nsf_id = 'UCSUu1lih2RifWkKtDOJdsBA'
k =  'UCn4sPeUomNGIr26bElVdDYg'

#print(requests.get('https://www.googleapis.com/youtube/v3/channels',{'id':nsf_id,'key':APIKEY}).json())
#live info#j = requests.get('https://www.googleapis.com/youtube/v3/videos',{'part':'contentDetails,liveStreamingDetails,snippet','id':'eHCxaeO4vM4','key':APIKEY}).json()
#all videos for channel(max)#j = requests.get('https://www.googleapis.com/youtube/v3/search',{'order':'date','part':'snippet','channelId':k,'maxResluts':25,'key':APIKEY}).json()
#print(json.dumps(j,indent=2,sort_keys=True))