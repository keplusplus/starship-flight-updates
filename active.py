import database, time, telebot
from threading import Thread

currently_active = {'closure':[],'tfr':[]}

def main(): #this should tell when closure/tfr is now or no longer active
    while True:
        print('Should listen on apis:',(currently_active['closure']!=[] and currently_active['tfr']!=[]))
        print(database.road_closure_active())
        if database.road_closure_active() != ():
            currently_active['closure'].append(database.road_closure_active())
            telebot.send_channel_message('missing closure now active')
        else:
            if currently_active['closure'] != []:
                telebot.send_channel_message('missing closure no longer active')
                currently_active['closure'] == []         
        time.sleep(20)

def start():
    Thread(target=main).start()
    pass