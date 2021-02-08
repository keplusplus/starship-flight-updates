import requests
import json
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

    def __init__(self):
        self.accounts = []
        self.latest_tweets = []
        # print(json.dumps(self.accounts, indent=2, sort_keys=False))

    def __get_account(username):
        response = requests.get(Twitter.lookup_endpoint + '?usernames=' + str.lower(username), headers=Twitter.headers).json()
        try:
            return response['data'][0]
        except KeyError:
            return

    def add_twitter_account(self, username):
        account = self.__get_account(username)
        if account not in self.accounts:
            self.accounts.append(account)
            return account

    def remove_twitter_account(self, username):
        account = self.__get_account(username)
        while account in self.accounts:
            self.accounts.remove(account)
