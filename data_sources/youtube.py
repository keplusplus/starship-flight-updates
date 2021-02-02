import requests
#https://developers.google.com/youtube/v3/docs
APIKEY = 'AIzaSyBVgZV4-_MzfS9oENPjuH8kX11OOv5Clzg'
nsf_id = 'UCSUu1lih2RifWkKtDOJdsBA'
#print(requests.get('https://www.googleapis.com/youtube/v3/channels',{'id':nsf_id,'key':APIKEY}).json())
print(requests.get('https://www.googleapis.com/youtube/v3/search',{'order':'date','part':'snippet','channelId':nsf_id,'maxResluts':25,'key':APIKEY}).json())