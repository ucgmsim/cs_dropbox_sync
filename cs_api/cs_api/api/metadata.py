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


@server.app.route(const.GET_UNIQUE_FAULTS, methods=["GET"])
@cross_origin(expose_headers=["Content-Type", "Authorization"])
@utils.endpoint_exception_handling(server.app)
def get_all_unique_faults():
    """
    Gets all the unique faults from every run on dropbox
    """
    server.app.logger.info(f"Received request at {const.GET_UNIQUE_FAULTS}")
    unique_faults = db.get_all_unique_faults()
    return flask.jsonify(unique_faults)


@server.app.route(const.GET_UNIQUE_SITES, methods=["GET"])
@cross_origin(expose_headers=["Content-Type", "Authorization"])
@utils.endpoint_exception_handling(server.app)
def get_all_unique_sites():
    """
    Gets all the unique sites from every run on dropbox
    """
    server.app.logger.info(f"Received request at {const.GET_UNIQUE_SITES}")
    unique_sites = db.get_all_unique_sites()
    return flask.jsonify(unique_sites)
