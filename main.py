from database import CameronCountyData, Database, FAAData
import message,datetime,time, schedule, active, telebot
from database import Database, CameronCountyData, FAAData, WikiData
from status import Status
from data_sources.weather import Weather
from data_sources.cameron_county import CameronCountyParser
from data_sources.faa import FAAParser
from data_sources.wikipedia import WikipediaParser
from data_sources import twitter
from data_sources import dotenv_parser
from logger import StarshipLogger
import logging
import sys

def daily_update(logger):
    logger.debug('>daily')
    try:
        ccp = CameronCountyParser()
        ccp.parse()
        CameronCountyData().append_cameroncounty(ccp.closures,False)
        faa = FAAParser()
        faa.parse()
        FAAData().append_faa(faa.tfrs,False)
        logger.debug('>collected & waiting')
        #make sure the message is sent exactly at 11:00 (UTC)
        wait = (datetime.datetime.combine(datetime.datetime.now().date(), Database().daily_message_time)-datetime.datetime.now()).total_seconds()
        if wait > 0:
            time.sleep(wait)
        message.send_message(message.daily_update_message(closures=CameronCountyData().road_closure_today(),tfrs=FAAData().faa_today(),weather=Weather().current_weather()),color=16767232)
    except Exception as e:
        message.ErrMessage().sendErrMessage('Error daily-message!\n\nException:\n' + str(e))

def regular_update(twit:twitter.Twitter, logger: StarshipLogger):
    logger.debug('>updating '+datetime.datetime.utcnow().strftime("%H:%M:%S %d-%m-%Y"))
    try:
        ccp = CameronCountyParser()
        ccp.parse()
        #ccp.closures.append({'begin': datetime.datetime(2021,4,2,9,53),'end': datetime.datetime(2021,4,2,9,54),'valid': True})
        CameronCountyData().append_cameroncounty(ccp.closures)

        faa = FAAParser()
        faa.parse()
        #faa.tfrs.append({'begin':datetime.datetime(2021,4,2,14,49),'end':datetime.datetime(2021,4,2,14,50),'fromSurface':True,'toAltitude':-1})
        FAAData().append_faa(faa.tfrs)

        wiki = WikipediaParser()
        wiki.parse()
        #wiki.starships.append({'name':'Test','firstSpotted':'test2021','rolledOut':'test','firstStaticFire':'test','maidenFlight':'test','decomissioned':'test','constructionSite':'test','status':'test','flights':-1})
        WikiData().append_history(wiki.starships)

        # active.manage_twitter(twit)
    except Exception as e:
        message.ErrMessage().sendErrMessage('Error regular-update!\n\nException:\n' + str(e))

#Database().reset_database()
def main():
    #daily_update()
    Database().setup_database()

    # Initialize logging
    args = str(sys.argv)
    if '--testing' in args or '-t' in args:
        logger = StarshipLogger(level = logging.DEBUG, broadcast = True)

        try:
            branch = dotenv_parser.get_value('.env','BRANCH') 
            logger.info('Starting Starship Flight Updates Bot (TESTING) on branch ' + branch)
        except ValueError:
            logger.info('Starting Starship Flight Updates Bot (TESTING)')
    else:
        logger = StarshipLogger(level = logging.INFO)
        logger.info('Starting Starship Flight Updates Bot (PROD)')
    # ------------------

    twit = twitter.Twitter(0, logger)
    twit.add_twitter_account('BocaChicaGal')
    twit.add_twitter_account('SpaceX')
    regular_update(twit, logger)
    active.start(twit, logger)
    calcDailyTime = datetime.datetime.combine(datetime.datetime.utcnow().date(),Database().daily_message_time)-datetime.timedelta(minutes=5)
    schedule.every().day.at(calcDailyTime.strftime('%H:%M')).do(daily_update, logger)
    logger.info('>Daily-Update Time: '+calcDailyTime.strftime('%H:%M'))
    schedule.every(15).to(25).minutes.do(regular_update, twit, logger)
    logger.debug('>starting main-main loop')
    while 1:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()