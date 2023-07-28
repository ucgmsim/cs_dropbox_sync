import flask
from flask_cors import cross_origin

from cs_api import server, utils
from cs_api import constants as const
from cs_api.db import db


@server.app.route(const.GET_TECTONIC_TYPES, methods=["GET"])
@cross_origin(expose_headers=["Content-Type", "Authorization"])
@utils.endpoint_exception_handling(server.app)
def get_tectonic_types():
    """
    Gets the tectonic types from the db
    """
    server.app.logger.info(f"Received request at {const.GET_TECTONIC_TYPES}")
    return flask.jsonify(db.get_tect_types())


@server.app.route(const.GET_GRID_SPACING, methods=["GET"])
@cross_origin(expose_headers=["Content-Type", "Authorization"])
@utils.endpoint_exception_handling(server.app)
def get_grid_spacing():
    """
    Gets the grid spacing from the db
    """
    server.app.logger.info(f"Received request at {const.GET_GRID_SPACING}")
    return flask.jsonify(db.get_grid_spacings())


@server.app.route(const.GET_RUN_TYPES , methods=["GET"])
@cross_origin(expose_headers=["Content-Type", "Authorization"])
@utils.endpoint_exception_handling(server.app)
def get_run_types():
    """
    Gets the possible run types from the db
    """
    server.app.logger.info(f"Received request at {const.GET_RUN_TYPES}")
    return flask.jsonify(db.get_run_types())


@server.app.route(const.GET_DATA_TYPES, methods=["GET"])
@cross_origin(expose_headers=["Content-Type", "Authorization"])
@utils.endpoint_exception_handling(server.app)
def get_data_types():
    """
    Gets the data types from the db
    """
    server.app.logger.info(f"Received request at {const.GET_DATA_TYPES}")
    return flask.jsonify(db.get_data_types())
