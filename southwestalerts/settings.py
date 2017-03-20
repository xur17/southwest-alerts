import os


class User:
    username = None
    password = None

    def __init__(self, username, password):
        self.username = username
        self.password = password


# Find all USERNAME# / PASSWORD# pairs and add the to the list of users to check
_index = 1
mailgun_api_key = os.environ['MAILGUN_API_KEY']
users = []
while os.environ.get('USERNAME{}'.format(_index)):
    user = User(os.environ['USERNAME{}'.format(_index)], os.environ['PASSWORD{}'.format(_index)])
    users.append(user)
    _index += 1
