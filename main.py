from database import CameronCountyData, Database, FAAData
import message,datetime,time, schedule, active, telebot
from database import Database, CameronCountyData, FAAData, WikiData
from status import Status
from data_sources.weather import Weather
from data_sources.cameron_county import CameronCountyParser
from data_sources.faa import FAAParser
from data_sources.wikipedia import WikipediaParser
from data_sources import twitter

def daily_update():
    print('>daily')
    try:
        ccp = CameronCountyParser()
        ccp.parse()
        CameronCountyData().append_cameroncounty(ccp.closures,False)
        faa = FAAParser()
        faa.parse()
        FAAData().append_faa(faa.tfrs,False)
        print('>collected & waiting')
        #make sure the message is sent exactly at 13:00
        wait = (datetime.datetime.now().replace(hour=13,minute=0,second=0,microsecond=0)-datetime.datetime.now()).total_seconds()
        if wait > 0:
            time.sleep(wait)
        message.send_message(message.daily_update_message(closures=CameronCountyData().road_closure_today(),tfrs=FAAData().faa_today(),weather=Weather().today_forecast()),color=16767232)
    except Exception as e:
        message.ErrMessage().sendErrMessage('Error daily-message!\n\nException:\n' + str(e))

def regular_update(twit:twitter.Twitter):
    print('>updating '+datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y"))
    try:
        ccp = CameronCountyParser()
        ccp.parse()
        #ccp.closures.append({'begin': datetime.datetime(2021,4,2,9,53),'end': datetime.datetime(2021,4,2,9,56),'valid': False})
        CameronCountyData().append_cameroncounty(ccp.closures)

        faa = FAAParser()
        faa.parse()
        #faa.tfrs.append({'begin':datetime.datetime(2021,4,2,14,49),'end':datetime.datetime(2021,4,2,14,50),'fromSurface':True,'toAltitude':-1})
        FAAData().append_faa(faa.tfrs)

        wiki = WikipediaParser()
        wiki.parse()
        #wiki.starships.append({'name':'Test','firstSpotted':'test','rolledOut':'test','firstStaticFire':'test','maidenFlight':'test','decomissioned':'test','constructionSite':'test','status':'test','flights':-1})
        WikiData().append_history(wiki.starships)

        active.manage_twitter(twit)
    except Exception as e:
        message.ErrMessage().sendErrMessage('Error regular-update!\n\nException:\n' + str(e))

#Database().reset_database()
def main():
    #daily_update()
    Database().setup_database()
    twit = twitter.Twitter(0)
    twit.add_twitter_account('BocaChicaGal')
    twit.add_twitter_account('SpaceX')
    regular_update(twit)
    active.start(twit)
    schedule.every().day.at("12:55").do(daily_update)
    schedule.every(15).to(25).minutes.do(regular_update, twit = twit)
    print('>starting main-main loop')
    while 1:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()