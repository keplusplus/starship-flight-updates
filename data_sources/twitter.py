from message import ErrMessage
import requests, telebot
from datetime import timedelta, datetime

from requests.models import Response
from data_sources import dotenv_parser
import logger

class Twitter:
    disabled = True

    tweet_endpoint = 'https://api.twitter.com/2/users/:id/tweets?exclude=retweets'
    lookup_endpoint = 'https://api.twitter.com/2/users/by'
    env = dotenv_parser.get_env('.env')

    try:
        headers = {
            'Authorization': 'Bearer ' + env['TWITTER_BEARER_TOKEN']
        }
    except KeyError as e:
        print(e)
        print('Check Twitter credentials in your .env file!')
    
    def __req_json(self, endpoint):
        if self.disabled:
            return { 'meta': { 'result_count': 0 } }

        try:
            self.logger.debug('[twitter] | GET {}'.format(endpoint))
            response = requests.get(endpoint, headers=Twitter.headers)
            self.logger.debug('[twitter] | {} Reponse: {}'.format(response.status_code, response.json()))
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error('Requesting Twitter API returned an Error!')
                self.logger.error('Check your bearer token in .env!')
                self.logger.error(response.json())
                return { 'meta': { 'result_count': 0 } }
        except Exception as e:
            self.logger.warning('[twitter] | Error occured in last request - {}'.format(str(e)))
            if e is not requests.ConnectionError:
                ErrMessage().sendErrMessage('Error Twitter-req-json!\n\nException:\n' + str(e))
            return None

    def __init__(self, timespan=0, logger=logger.StarshipLogger('twitter.log')):
        self.accounts = []
        self.latest_tweets = {}
        self.timespan = timespan
        self.init_time = datetime.utcnow()
        self.last_update = {}
        self.logger = logger

    def __get_account(self, username):
        response = self.__req_json(Twitter.lookup_endpoint + '?usernames=' + str.lower(username))
        if response is None:
            return None
        try:
            return response['data'][0]
        except KeyError:
            return
    
    def __get_tweets(self, user_id):
        try:
            latest = self.latest_tweets[user_id]
            response = self.__req_json(Twitter.tweet_endpoint.replace(':id', user_id) + '&since_id=' + latest)
        except KeyError:
            dt = self.init_time - timedelta(minutes=self.timespan)
            dtstr = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            response = self.__req_json(Twitter.tweet_endpoint.replace(':id', user_id) + '&start_time=' + dtstr)
        
        if response is None:
            return None

        if response['meta']['result_count'] > 0:
            self.latest_tweets[user_id] = response['meta']['newest_id']
            return response['data']
        else:
            return []

    def add_twitter_account(self, username):
        account = self.__get_account(username)
        if account is None:
            return None
        if account not in self.accounts:
            self.accounts.append(account)
        return account

    def remove_twitter_account(self, username):
        account = self.__get_account(username)
        if account is None:
            return None
        while account in self.accounts:
            self.accounts.remove(account)

    def update(self):
        update = {}
        for account in self.accounts:
            tweets = self.__get_tweets(account['id'])
            if tweets is None:
                return None
            update[account['username']] = tweets
        self.last_update = update
        return update
    
    def get_Name(self, username:str):
        for account in self.accounts:
            if account['username'] == username:
                return account['name']
        return None

