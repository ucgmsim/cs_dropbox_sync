import flask
from flask_cors import cross_origin

from cs_api import server, utils
from cs_api import constants as const
from dropbox_rclone import dropbox_reading


@server.app.route(const.GET_META_RUNS, methods=["GET"])
@cross_origin(expose_headers=["Content-Type", "Authorization"])
@utils.endpoint_exception_handling(server.app)
def get_available_cybershake_runs():
    """
    Gets the currently available cybershake runs that are on dropbox
    """
    server.app.logger.info(f"Received request at {const.GET_META_RUNS}")
    return flask.jsonify(dropbox_reading.find_available_runs())
