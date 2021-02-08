import requests

class Twitter:
    tweet_endpoint = 'https://api.twitter.com/2/users/:id/tweets'
    lookup_endpoint = 'https://api.twitter.com/2/users/by'
    headers = {
        'Authorization': 'Bearer' + 'AAAAAAAAAAAAAAAAAAAAAOQxMgEAAAAA%2F4OCxCwP6%2FaHi8vM%2BE7U74lvVk4%3Dh4InETTGnW856zQToV97mUMSvxtiPJgigtxyR9aTbR8ekoj77n'
    }

    def __init__(self):
        self.accounts = []
        self.__get_account_id('GameRate_yt')

    def add_twitter_account(self, username):
        pass

    def remove_twitter_account(self, username):
        pass

    def get_twitter_accounts(self):
        return self.accounts

    def __get_account_id(self, username):
        response = requests.get(Twitter.lookup_endpoint + '?usernames=' + str.lower(username), headers=Twitter.headers)
        print(response)
