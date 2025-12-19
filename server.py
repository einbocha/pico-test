from flask import Flask, abort, request
from flask_httpauth import HTTPBasicAuth
import json
import os
from logging.handlers import RotatingFileHandler
import logging

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

log_fstring = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
mbyte = 100 * (1024 * 1024)

file_handler = RotatingFileHandler('server.log', maxBytes=mbyte)
file_handler.setFormatter(logging.Formatter(log_fstring))

app.logger.addHandler(file_handler)
app.logger.setLevel(logging.DEBUG)

werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.addHandler(file_handler)
werkzeug_logger.setLevel(logging.DEBUG)

app.logger.info("🚀 Server startet")

if not os.path.exists(CONFIG):
    default_config = {
        'users': [
            {'name': 'admin', 'pwd': '123', 'friends': ['admin']},
        ]
    }
    write_config(default_config)

if not config_get_user('admin'):
    app.logger.critical('Admin user missing!')

if not os.path.exists(STATE):
    default_state = {}
    for user in config_get_user():
        username = user['name']
        default_state[username] = {
            'requested': False,
            'state': []
        }
    write_state(default_state)


def update_state(username, rec, change):
    state = read_state()

    state[rec]['state'] = change

    if username != rec:
        state[rec]['requested'] = False

    write_state(state)

    app.logger.info(f'{username}: "{change}" -> rec')


def msg_to_state(username, rec, msg):
    state = read_state()

    state[rec]['state'].append(msg)

    if username != rec:
        state[rec]['requested'] = False

    write_state(state)

    app.logger.info(f'{username}: "{msg}" -> rec')


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

    state[username]['requested'] = True

    write_state(state)

    return state[username]


@app.route('/admin_view')
@auth.login_required
def super_state():
    username = auth.current_user()
    if username != 'admin':
        abort(401)

    state = read_state()

    return state


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

    msg_to_state(username, rec, msg)

    return ""


@app.route('/update_state', methods=['POST'])
@auth.login_required
def update_state_of():
    username = auth.current_user()

    friends = config_get_user(username)['friends']

    data = request.get_json()

    rec = data['receiver']
    state = data['new_state']

    if rec not in friends:
        abort(400)

    update_state(username, rec, state)

    return ""


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
