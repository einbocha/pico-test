from flask import Flask, abort, request
from flask_httpauth import HTTPBasicAuth
import json
import os

CONFIG = 'server_config.json'
STATE = 'server_state.json'


def read_state():
    with open(STATE, 'r') as f:
        json_string = f.read()

    state = json.loads(json_string)

    return state


def write_state(state):
    with open(STATE, 'w') as f:
        json.dump(state, f, indent=2)


def read_config():
    with open(CONFIG, 'r') as f:
        json_string = f.read()

    state = json.loads(json_string)

    return state


def write_config(config):
    with open(CONFIG, 'w') as f:
        json.dump(config, f, indent=2)


def config_get_user(username=None):
    config = read_config()

    users = config['users']

    if not username:
        return users

    for user in users:
        if username == user['name']:
            return user

    return None


app = Flask(__name__)
auth = HTTPBasicAuth()

if not os.path.exists(CONFIG):
    default_config = {
        'users': [
            {'name': 'admin', 'pwd': '123', 'friends': ['admin']},
        ]
    }
    write_config(default_config)

if not config_get_user('admin'):
    print('Admin user missing!')

if not os.path.exists(STATE):
    default_state = {}
    for user in config_get_user():
        username = user['name']
        default_state[username] = {
            'requested': False,
            'state': []
        }
    write_state(default_state)


def update_state(username, change):
    state = read_state()

    state[username]['state'] = change

    write_state(state)


def msg_to_state(username, msg):
    state = read_state()

    state[username]['state'].append(msg)

    write_state(state)


@auth.verify_password
def verify_password(username, password):
    config = read_config()

    for user in config['users']:
        if username == user['name'] and password == user['pwd']:
            return username

    return None


@app.route('/')
@auth.login_required
def personal_state():
    username = auth.current_user()

    state = read_state()

    return state[username]


@app.route('/send_msg', methods=['POST'])
@auth.login_required
def send_msg_to():
    username = auth.current_user()

    friends = config_get_user(username)['friends']

    data = request.get_json()

    rec = data['receiver']
    msg = data['msg']

    if rec not in friends:
        abort(400)

    msg_to_state(rec, msg)

    return ""


@app.route('/admin_view')
@auth.login_required
def super_state():
    username = auth.current_user()
    if username != 'admin':
        abort(401)

    state = read_state()

    return state


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
