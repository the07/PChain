import json
import requests
import hashlib
import sys
import socket

from user import User

FULL_NODE_PORT = "30609"
NODES_URL = "http://{}:{}/nodes" # GET RETURNS ALL THE NODES, POST ADDS NODE
USERS_URL = "http://{}:{}/users" # GET RETURNS ALL THE USER, POST ADDS NEW USER to chain.users
CREATE_USER_URL = "http://{}:{}/create" # POST ADD NEW USER TO UNCONFIRMED USERS
VIEW_USER_URL = "http://{}:{}/view/{}" # GET RETURNS USER DATA FROM USERS
EDIT_USER_URL = "http://{}:{}/edit/{}" # POST pops user from USER, ADDS NEW DATA TO UNCONFIRMED USER
MINE_URL = "http://{}:{}/mine" # GET moves, user from unconfirmed_users to users # PROOF OF WORK COMES IN HERE

class Client:

    def __init__(self):

        self.node = self.my_node()
        self.run_client()

    def run_client(self):

        while True:
            # ASSERT TRY AND CATCH EXCEPTIONS: ASSERTION ERROR AND VALUE ERROR
            print ("1. Create User\n")
            print ("2. View User - (Need address)\n")
            print ("3. Edit User - (Need address)\n")
            print ("4. View All Users\n")
            print ("5. View Nodes\n")
            print ("6. Mine\n")
            choice = int(input("Enter your choice: "))

            if choice == 1:
                self.create_user()
            if choice == 2:
                self.view_user()
            if choice == 3:
                self.edit_user()
            if choice == 4:
                self.view_all_users()
            if choice == 5:
                self.view_full_nodes()
            if choice == 6:
                self.mine()

        sys.exit()


    def my_node(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        my_node = s.getsockname()[0]
        s.close()
        return my_node

    def create_user(self):
        name = str(input("Enter you name(Cannot be empty): "))
        assert name
        address = hashlib.sha256(name.encode('utf-8')).hexdigest()
        user = User(address, name)

        data = user.__dict__

        # TODO : try and catch exceptions
        url = CREATE_USER_URL.format(self.node, FULL_NODE_PORT)
        response = requests.post(url, json=data)

        if response.status_code == 200:
            print ('User created, will be added to the chain when node is mined.')

    def edit_user(self):

        address = str(input("Enter the address you want to edit: "))
        assert address
        attribute = str(input("Enter a new attribute: "))
        value = str(input("Enter value: "))
        user_data = {attribute: value}
        data = {
            "data": user_data,
        }
        url = EDIT_USER_URL.format(self.node, FULL_NODE_PORT, address)
        response = requests.post(url, json=data)

        if response.status_code == 200:
            print ("User successfully updated, changes will reflect in after mining.")

    def view_user(self):
        # GET TO /user/<address>
        address = str(input("Enter user address: "))
        assert address
        url = VIEW_USER_URL.format(self.node, FULL_NODE_PORT, address)
        response = requests.get(url)
        user = json.loads(response.json()['user'])

        print ("User Name: {}, User Balance: {}, User Data: {}".format(user['_name'], user['_balance'], user['_data']))
        print ("\n")

    def view_all_users(self):

        url = USERS_URL.format(self.node, FULL_NODE_PORT)
        response = requests.get(url)
        index = 1
        for user in response.json():
            print ("User #{}".format(index))
            print ("User Name: {}, User Address: {}, User Balance: {}, User Data: {}".format(user['_name'], user['_address'],user['_balance'], user['_data']))
            index += 1
        print ("\n")

    def view_full_nodes(self):
        # GET TO /nodes
        url = NODES_URL.format(self.node, FULL_NODE_PORT)
        response = requests.get(url)
        print (response.json()['full_nodes'])
        print ("\n")

    def mine(self):

        url = MINE_URL.format(self.node, FULL_NODE_PORT)
        print ('Mining, chech node')
        response = requests.get(url)
        print (response.json()['message'])


if __name__ == '__main__':

    client = Client()
