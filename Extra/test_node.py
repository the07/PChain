import json
import socket

from user import User
from blockchain import Peopleschain

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

    full_nodes = set()
    app = Klein()

    def __init__(self, host=None):

        if host is None:
            self.peopleschain = Peopleschain()
            self.node = self.get_my_node()
            self.full_nodes.add(self.node)
        else:
            self.node = self.get_my_node()
            self.add_node(host)
            self.request_nodes(host, FULL_NODE_PORT)
            self.broadcast_node()
            remote_users = self.synchronize()
            self.peopleschain = Peopleschain(remote_users)
            self.full_nodes.add(self.node)

        print ("\n Full Node Server Started... \n\n")
        self.app.run('0.0.0.0', FULL_NODE_PORT)

    def get_my_node(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        my_node = s.getsockname()[0]
        s.close()
        return my_node

    def request_nodes(self, host, port):
        url = NODES_URL.format(host, port)
        try:
            response = requests.get(url)
            if response.status_code == 200:
                all_nodes = response.json()
                return all_nodes
        except requests.exceptions.RequestException as re:
            pass
        return None

    def request_nodes_from_all(self):
        full_nodes = self.full_nodes.copy()
        bad_nodes = set()

        for node in full_nodes:
            all_nodes = self.request_nodes(node, FULL_NODE_PORT)
            if all_nodes is not None:
                full_nodes = full_nodes.union(all_nodes['full_nodes'])
            else:
                bad_nodes.add(node)

        self.full_nodes = full_nodes

        for node in bad_nodes:
            self.remove_node(node)

        bad_nodes.clear()
        return

    def remove_node(self, node):
        pass

    def broadcast_node(self):

        bad_nodes = set()
        data = {
            "host": self.node
        }

        for node in self.full_nodes:
            if node == self.node:
                continue
            url = NODES_URL.format(node, FULL_NODE_PORT)
            try:
                requests.post(url, json=data) #TODO check for response and proceed accordingly
            except requests.exceptions.RequestException as re:
                bad_nodes.add(node)

        for node in bad_nodes:
            self.remove_node(node)
        bad_nodes.clear()
        return

    def synchronize(self):

        self.request_nodes_from_all()
        longest = 0
        for node in self.full_nodes:
            if node == self.node:
                continue
            url = USERS_URL.format(node, FULL_NODE_PORT)
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    users_list = response.json()
                    if len(users_list) > longest:
                        longest = len(users_list)
                        users = []
                        for user_list in users_list:
                            user = User(user_list['_address'], user_list['_name'], user_list['_balance'], user_list['_data'])
                            users.append(user)
            except requests.exceptions.RequestException as re:
                pass
        return users

    def add_node(self, node):

        if node == self.node:
            return

        if node not in self.full_nodes:
            self.full_nodes.add(node)

    def broadcast_users(self, user_list):
        bad_nodes = set()
        data = [user.__dict__ for user in user_list]
        for node in self.full_nodes:
            if node == self.node:
                continue
            url = USERS_URL.format(node, FULL_NODE_PORT)
            try:
                requests.post(url, json=data)
            except requests.exceptions.RequestException as re:
                bad_nodes.add(node)

        for node in bad_nodes:
            self.remove_node(node)
        bad_nodes.clear()
        return

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
        users_list = json.loads(request.content.read().decode('utf-8'))
        print (users_list)
        for user_list in users_list:
            user = User(user_list['_address'], user_list['_name'], user_list['_balance'], user_list['_data'])
            self.peopleschain.add_user(user)
        response = {
            "message": "Blockchain updated"
        }
        return json.dumps(response).encode('utf-8')

    @app.route('/create', methods=['POST'])
    def create_user(self, request):
        user_json = json.loads(request.content.read().decode('utf-8'))
        user_address = user_json['_address']
        if self.peopleschain.get_user_by_address(user_address): #TODO: should also check for user in unconfirmed users
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
        user = self.peopleschain.get_user_by_address(address)
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
        user = self.peopleschain.get_user_by_address(address)
        if user is not None:
            #TODO: code to edit a user profile
            # pop user from chain.users,
            # create new user object with new data but same address
            # push to unconfirmed users
            address = user.address
            name = user.name
            balance = user.balance
            data = user.data
            balance -= 20 #Charge 20 coins as transaction fees
            self.peopleschain.remove_user_by_address(address)
            new_user_data_json = json.loads(request.content.read().decode('utf-8'))
            if 'name' in new_user_data_json:
                name = new_user_data_json['name']
            if 'data' in new_user_data_json:
                for each_item in new_user_data_json['data']:
                    data[each_item] = new_user_data_json['data'][each_item]
            edited_user = User(address, name, balance, data)
            self.peopleschain.push_unconfirmed_user(edited_user)
            response = {
                "message": "Profile updated, update will reflect once the profile is mined."
            }
            return json.dumps(response).encode('utf-8')
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
        self.broadcast_users(broadcast_user_list)

        return json.dumps(response).encode('utf-8')

if __name__ == '__main__':

    host = str(input("Enter host: (Leave blank to start a new chain)"))
    if host == '':
        node = Node()
    else:
        node = Node(host)
