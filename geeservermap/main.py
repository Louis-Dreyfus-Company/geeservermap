from flask import Flask, render_template, url_for, request, jsonify
# from dotenv import load_dotenv
import argparse
from .async_jobs import asyncgee
import uuid
import webbrowser

MESSAGES = {}

# load_dotenv()  # Load environment variable from .env
PORT = 8018

parser = argparse.ArgumentParser()
parser.add_argument('--port', default=PORT, help='port')

app = Flask(__name__)

@app.route("/")
def map():
    return render_template('map.html')

@app.route('/add_layer', methods=['GET'])
def add_layer():
    url = request.args.get('url', type=str)
    name = request.args.get('name', type=str)
    visible = request.args.get('visible', type=bool)
    opacity = request.args.get('opacity', type=float)
    layer = {
        'url': url, 'name': name, 'visible': visible,
        'opacity': opacity
    }
    job_id = uuid.uuid4().hex
    print(job_id)
    MESSAGES[job_id] = layer
    return jsonify({'job_id': job_id})

@app.route('/get_message', methods=['GET'])
def get_message():
    job_id = request.args.get('id', type=str)
    return MESSAGES.get(job_id)

@app.route('/messages')
def messages():
    return jsonify(MESSAGES)

def run():
    args = parser.parse_args()
    port = args.port
    # webbrowser.open(f'http://localhost:{port}')
    app.run(debug=True, port=port)