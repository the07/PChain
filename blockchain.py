import hashlib
import logging
import threading
from time import time

from user import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Peoplechain():

    users = []
    unconfirmed_users = []

    def __init__(self, users=None):

        self.users_lock = threading.Lock()

        if users is None:

            genesis_user = self.get_genesis_user()
            self.add_user(genesis_user)

        else:

            for user in users:
                self.add_user(user)

    def get_genesis_user(self):

        print ("###########################################################\n")
        print ("#################### CREATING GENESIS USER ################\n")

        genesis_user_address = '0409eb9224f408ece7163f40a33274d99ab6b3f60e41b447dd45fcc6371f57b88d9d3583c358b1ea8aea4422d17c57de1418554d3a1cd620ca4cb296357888ea596'
        genesis_user_name = 'Network'
        genesis_user_balance = 100000000000000
        genesis_user_data = {
            "Location": "Bangalore"
        }

        genesis_user = User(genesis_user_address, genesis_user_name, genesis_user_balance, genesis_user_data)
        print ("#################### GENESIS USER CREATED ################\n")
        return genesis_user

    def add_user(self, user):
        with self.users_lock:
            self.users.append(user)
            return True
        return False

    def push_unconfirmed_user(self, user):
        self.unconfirmed_users.append(user)
        return True
    
    def get_last_user(self):
        return self.users[-1]

    def get_size(self):
        return len(self.users)

    def get_user_by_address(self, address):
        for user in self.users:
            if user.address == address:
                return user
        return False

    def get_all_users(self):
        return self.users

    def __str__(self):
        return str(self.__dict__)

if __name__ == '__main__':
    pass
