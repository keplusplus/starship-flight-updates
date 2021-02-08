import requests
import json

class Twitter:
    tweet_endpoint = 'https://api.twitter.com/2/users/:id/tweets'
    lookup_endpoint = 'https://api.twitter.com/2/users/by'
    headers = {
        'Authorization': 'Bearer ' + 'AAAAAAAAAAAAAAAAAAAAAOQxMgEAAAAA%2F4OCxCwP6%2FaHi8vM%2BE7U74lvVk4%3Dh4InETTGnW856zQToV97mUMSvxtiPJgigtxyR9aTbR8ekoj77n'
    }

    def __init__(self):
        self.accounts = []
        # print(json.dumps(self.accounts, indent=2, sort_keys=False))

    def add_twitter_account(self, username):
        account = self.__get_account(username)
        if account not in self.accounts:
            self.accounts.append(account)
            return account

    def remove_twitter_account(self, username):
        account = self.__get_account(username)
        while account in self.accounts:
            self.accounts.remove(account)

    def get_twitter_accounts(self):
        return self.accounts

    def __get_account(self, username):
        response = requests.get(Twitter.lookup_endpoint + '?usernames=' + str.lower(username), headers=Twitter.headers).json()
        try:
            return response['data'][0]
        except KeyError:
            return

Twitter()