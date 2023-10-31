"""TODO Missing docstring."""

# from dotenv import load_dotenv
import argparse
import uuid

from flask import Flask, jsonify, render_template, request

MESSAGES = {}

# load_dotenv()  # Load environment variable from .env
PORT = 8018
WIDTH = 800
HEIGHT = 600

parser = argparse.ArgumentParser()
parser.add_argument(
    "--port", default=PORT, help=f"Port in which the app will run. Defaults to {PORT}"
)
parser.add_argument(
    "--width", default=WIDTH, help=f"Width of the map's pane. Defaults to {WIDTH} px"
)
parser.add_argument(
    "--height",
    default=HEIGHT,
    help=f"Height of the map's pane. Defaults to {HEIGHT} px",
)

app = Flask(__name__)


def register_map(width, height):
    """Register the index endpoint, allowing the user to pass a height and width."""

    @app.route("/")
    def map():
        return render_template("map.html", width=width, height=height)


@app.route("/add_layer", methods=["GET"])
def add_layer():
    """TODO Missing docstring."""
    url = request.args.get("url", type=str)
    name = request.args.get("name", type=str)
    visible = request.args.get("visible", type=bool)
    opacity = request.args.get("opacity", type=float)
    layer = {"url": url, "name": name, "visible": visible, "opacity": opacity}
    job_id = uuid.uuid4().hex
    print(job_id)
    MESSAGES[job_id] = layer
    return jsonify({"job_id": job_id})


@app.route("/get_message", methods=["GET"])
def get_message():
    """TODO Missing docstring."""
    job_id = request.args.get("id", type=str)
    return MESSAGES.get(job_id)


@app.route("/messages")
def messages():
    """TODO Missing docstring."""
    return jsonify(MESSAGES)


def run():
    """TODO Missing docstring."""
    args = parser.parse_args()
    port = args.port
    register_map(width=args.width, height=args.height)
    # webbrowser.open(f'http://localhost:{port}')
    app.run(debug=True, port=port)
