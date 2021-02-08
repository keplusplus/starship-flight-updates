import requests
from datetime import timedelta, datetime

from requests.models import Response
from data_sources import dotenv_parser

class Twitter:
    tweet_endpoint = 'https://api.twitter.com/2/users/:id/tweets'
    lookup_endpoint = 'https://api.twitter.com/2/users/by'
    env = dotenv_parser.get_env('.env')
    try:
        headers = {
            'Authorization': 'Bearer ' + env['TWITTER_BEARER_TOKEN']
        }
    except KeyError as e:
        print('Cannot create Twitter object!')
        print(e)
        print('Check you .env file!')
        exit(1)

    def __init__(self, timespan):
        self.accounts = []
        self.latest_tweets = {}
        self.timespan = timespan

    def __get_account(self, username):
        response = requests.get(Twitter.lookup_endpoint + '?usernames=' + str.lower(username), headers=Twitter.headers).json()
        try:
            return response['data'][0]
        except KeyError:
            return
    
    def __get_tweets(self, user_id):
        try:
            latest = self.latest_tweets[user_id]
            response = requests.get(Twitter.tweet_endpoint.replace(':id', user_id) + '?since_id=' + latest, headers=Twitter.headers).json()
        except KeyError:
            dt = datetime.utcnow() - timedelta(minutes=self.timespan)
            dtstr = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            response = requests.get(Twitter.tweet_endpoint.replace(':id', user_id) + '?start_time=' + dtstr, headers=Twitter.headers).json()

        if response['meta']['result_count'] > 0:
            self.latest_tweets[user_id] = response['meta']['newest_id']
            return response['data']
        else:
            return []

    def add_twitter_account(self, username):
        account = self.__get_account(username)
        if account not in self.accounts:
            self.accounts.append(account)
            return account

    def remove_twitter_account(self, username):
        account = self.__get_account(username)
        while account in self.accounts:
            self.accounts.remove(account)
