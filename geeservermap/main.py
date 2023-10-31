"""Setup the flask routes and start the server."""

import argparse
import uuid

from flask import Flask, jsonify, render_template, request

MESSAGES = {}
"saved message from the run jobs"

PORT = 8018
"The default port to run the server on."

WIDTH = 800
"The default width of the map's pane in pixels."

HEIGHT = 600
"The default height of the map's pane in pixels."

# parse the parameters from the command line call
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

# start the Flask application
app = Flask(__name__)


def register_map(width: int, height: int):
    """Register the index endpoint, allowing the user to pass a height and width.

    Args:
        width: The width of the map's pane in pixels.
        height: The height of the map's pane in pixels.
    """

    @app.route("/")
    def map():
        return render_template("map.html", width=width, height=height)


@app.route("/add_layer", methods=["GET"])
def add_layer():
    """Add a layer to the map."""
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
    """Get the saved message related to a specific job as a json output."""
    job_id = request.args.get("id", type=str)
    return MESSAGES.get(job_id)


@app.route("/messages")
def messages():
    """Get all the saved message related as a json output."""
    return jsonify(MESSAGES)


def run():
    """Start the map in the Flask server."""
    args = parser.parse_args()
    port = args.port
    register_map(width=args.width, height=args.height)
    app.run(debug=True, port=port)
