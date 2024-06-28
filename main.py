import os
import json
import socket
import threading
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from datetime import datetime

app = Flask(__name__)


STORAGE_FOLDER = 'storage'
os.makedirs(STORAGE_FOLDER, exist_ok=True)
DATA_FILE = os.path.join(STORAGE_FOLDER, 'data.json')


if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({}, f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/message', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        username = request.form['username']
        user_message = request.form['message']
        data = {
            'username': username,
            'message': user_message
        }

        send_to_socket_server(data)
        return redirect(url_for('index'))
    return render_template('message.html')

@app.route('/message.html')
def message_html():
    return redirect(url_for('message'))

def send_to_socket_server(data):
    udp_ip = "127.0.0.1"
    udp_port = 5000
    message = json.dumps(data).encode('utf-8')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message, (udp_ip, udp_port))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

def socket_server():
    udp_ip = "127.0.0.1"
    udp_port = 5000
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((udp_ip, udp_port))

    while True:
        data, addr = sock.recvfrom(1024)
        if data:
            message_dict = json.loads(data.decode('utf-8'))
            save_message(message_dict)

def save_message(message_dict):
    timestamp = datetime.now().isoformat()
    with open(DATA_FILE, 'r+') as f:
        data = json.load(f)
        data[timestamp] = message_dict
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

def start_socket_server():
    socket_thread = threading.Thread(target=socket_server)
    socket_thread.start()

if __name__ == '__main__':
    start_socket_server()
    app.run(debug=True, port=3000)
