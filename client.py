import json
import requests
import hashlib
import sys
import socket

from user import User

FULL_NODE_PORT = "30609"
NODES_URL = "http://{}:{}/nodes" # GET RETURNS ALL THE NODES, POST ADDS NODE
USERS_URL = "http://{}:{}/users" # GET RETURNS ALL THE USER, POST ADDS NEW USER
USER_URL = "http://{}:{}/user/{}" # GET RETURNS USER DATA, POST EDITS USER DATA
MINE_URL = "http://{}:{}/mine"
USER_CHANGE_URL = "http://{}:{}/mine/{}"

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

        sys.exit()


    def my_node(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        my_node = s.getsockname()[0]
        s.close()
        return my_node

    def create_user(self):
        # POST TO /users
        # GET TO /mine
        name = str(input("Enter you name(Cannot be empty): "))
        assert name
        address = hashlib.sha256(name.encode('utf-8')).hexdigest()
        user = User(address, name)

        print (user.address)

        data = {
            "user": user.to_json(),
            "node": self.node
        }

        # TODO : try and catch exceptions
        url = USERS_URL.format(self.node, FULL_NODE_PORT)
        response = requests.post(url, json=data)

        if response.status_code == 200:
            print ('New User Successfully created')

            print ('Mining new user to the network')
            mine_url = MINE_URL.format(self.node, FULL_NODE_PORT)
            mine_response = requests.get(mine_url)

            print (mine_response.json()['message'])
            print ("\n")

    def edit_user(self):
        # POST TO /user/<address>
        # GET TO /mine/<address>
        address = str(input("Enter the address you want to edit: "))
        assert address
        attribute = str(input("Enter a new attribute: "))
        value = str(input("Enter value: "))
        user_data = {attribute: value}
        new_name = str(input("Enter new name: "))
        data = {
            "name": new_name,
            "data": user_data,
            "host": self.node
        }
        url = USER_URL.format(self.node, FULL_NODE_PORT, address)
        response = requests.post(url, json=data)

        if response.status_code == 200:
            print ("User successfully updated")

            print ("Mining changes to other nodes")
            user_change_url = USER_CHANGE_URL.format(self.node, FULL_NODE_PORT, address)
            change_response = requests.get(user_change_url)

            print (change_response.json()['message'])
            print ('\n')


    def view_user(self):
        # GET TO /user/<address>
        address = str(input("Enter user address: "))
        assert address
        url = USER_URL.format(self.node, FULL_NODE_PORT, address)
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


if __name__ == '__main__':

    client = Client()
