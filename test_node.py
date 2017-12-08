import json
import socket

from user import User
from blockchain import Peoplechain

import requests
from klein import Klein

FULL_NODE_PORT = "30609"
NODES_URL = "http://{}:{}/nodes" # GET RETURNS ALL THE NODES, POST ADDS NODE
USERS_URL = "http://{}:{}/users" # GET RETURNS ALL THE USER, POST ADDS NEW USER to chain.users
CREATE_USER_URL = "http://{}:{}/create" # POST ADD NEW USER TO UNCONFIRMED USERS
VIEW_USER_URL = "http://{}:{}/view/{}" # GET RETURNS USER DATA FROM USERS
EDIT_USER_URL = "http://{}:{}/edit/{}" # POST pops user from USER, ADDS NEW DATA TO UNCONFIRMED USER GET just pops the data from USERS
MINE_URL = "http://{}:{}/mine" # GET moves, user from unconfirmed_users to users # PROOF OF WORK COMES IN HERE

class Node:

    def __init__():
        pass

    def add_node(self, node):
        pass

    def broadcast_users(self, user_list):
        pass

    @app.route('/nodes', methods=['GET'])
    def get_nodes(self, request):
        response = {
            "full_nodes": list(self.full_nodes)
        }
        return json.dumps(response).encode('utf-8')

    @app.route('/nodes', methods=['POST'])
    def post_node(self, request):
        request = json.loads(request.content.read().decode('utf-8'))
        host = request['host']
        self.add_node(host) #TODO: create a add_node function
        response = {
            "message": "Node Register"
        }
        return json.dumps(response).encode('utf-8')

    @app.route('/users', methods=['GET'])
    def get_users(self, request):
        return json.dumps([user.__dict__ for user in self.peopleschain.get_all_users()]).encode('utf-8')

    @app.route('/users', methods=['POST'])
    def post_users(self, request):
        users = []
        users_list = json.loads(request.content.read().decode('utf-8'))
        for user_list in users_list:
            user = User(user_list['_address'], user_list['_name'], user_list['_balance'], user_list['_data'])
            self.peopleschain.add_user(user)
        response = {
            "message": "Blockchain updated"
        }
        return json.dumps(response).encode('utf-8')

    @app.route('/create', methods=['POST'])
    def create_user(self, request):
        body = json.loads(request.content.read().decode('utf-8'))
        user_json = json.loads(body['user'])
        user_address = user_json['_address']
        if self.peopleschain.get_user_by_address(user_address):
            response = {
                "message": "User already exists"
            }
            return json.dumps(response)
        else:
            user = User(user_json['_address'], user_json['_name'], user_json['_balance'], user_json['_data'])
            self.peopleschain.push_unconfirmed_user(user)
            print ("New user data available, mine to add to chain")
            response = {
                "message": "User created, will be added in the next mine"
            }
            return json.dumps(response).encode('utf-8')

    @app.route('/view/<address>', methods=['GET'])
    def get_user_by_address(self, request, address):
        user = self.peoplechain.get_user_by_address(address)
        if user is not None:
            response = {
                "user": user.to_json()
            }
            return json.dumps(response).encode('utf-8')
        else:
            response = {
                "message": "User not found"
            }
            return json.dumps(response).encode('utf-8')


    @app.route('/edit/<address>', methods=['POST'])
    def edit_user_by_address(self, request, address):
        #TODO : implement signatures to restrict access
        user = self.peoplechain.get_user_by_address(address)
        if user is not None:
            #TODO: code to edit a user profile
            # pop user from chain.users,
            # create new user object with new data but same address
            # push to unconfirmed users
        else:
            response = {
                "message": "User Not Found"
            }
            return json.dumps(response).encode('utf-8')

    @app.route('/mine', methods=['GET'])
    def mine(self, request):
        if len(self.peopleschain.unconfirmed_users) == 0:
            response = {
                "message": "No users to mine"
            }
            return json.dumps(response).encode('utf-8')
        broadcast_user_list = self.peopleschain.unconfirmed_users.copy()
        while self.peopleschain.unconfirmed_users:
            user = self.peopleschain.unconfirmed_users.pop(0)
            self.peopleschain.add_user(user)

        print ('Users mined, now broadcasting to network...')
        #TODO: implement proof of work

        response = {
            "message": "Users mined into the blockchain"
        }
        self.broadcast_users(broadcast_user_list) #TODO: create a function to broadcast a list of users

        return json.dumps(response).encode('utf-8')
