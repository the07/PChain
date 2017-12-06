import json

class User:

    def __init__(self, address, name, balance=None, data=None):
        # Add option for a signature ( For security )
        self._address = address
        self._name = name
        if balance is not None:
            self._balance = balance
        else:
            self._balance = 100
        if data is not None:
            self._data = data
        else:
            self._data = {}

    @property
    def address(self):
        return self._address

    @property
    def name(self):
        return self._name

    @property
    def balance(self):
        return self._balance

    @property
    def data(self):
        return self._data

    @classmethod
    def from_json(cls, user_json):
        user = cls.__init__(user_json['_address'], user_json['_name'], user_json.get('_balance', None), user_json.get('_data', None))
        return user

    def setname(self, value):
        self._name = value
        return

    def setbalance(self, value):
        self._balance = value
        return

    def setdata(self, value):
        self._data = value
        return

    def to_json(self):
        return json.dumps(self, default=lambda o: {key: value for key, value in o.__dict__.items()}, sort_keys=True)

    def __repr__(self):
        return "<User {}>".format(self._address)

    def __str__(self):
        return str(self.__dict__)

if __name__ == '__main__':
    pass
