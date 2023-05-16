import flask
import yaml
from flask_cors import cross_origin

from cs_api import server, utils
from cs_api import constants as const


@server.app.route(const.GET_TECTONIC_TYPES, methods=["GET"])
@cross_origin(expose_headers=["Content-Type", "Authorization"])
@utils.endpoint_exception_handling(server.app)
def get_tectonic_types():
    """
    Gets the tectonic types from the metadata yaml file
    """
    server.app.logger.info(f"Received request at {const.GET_TECTONIC_TYPES}")
    with open(const.METADATA_FILE, "r") as f:
        run_metadata = yaml.safe_load(f)
    # Get all unique tectonic types from the metadata file
    tectonic_types = {tect_type for run in run_metadata.values() for tect_type in run["tectonic_types"]}
    return flask.jsonify(sorted(list(tectonic_types)))


@server.app.route(const.GET_GRID_SPACING, methods=["GET"])
@cross_origin(expose_headers=["Content-Type", "Authorization"])
@utils.endpoint_exception_handling(server.app)
def get_grid_spacing():
    """
    Gets the grid spacing from the metadata yaml file
    """
    server.app.logger.info(f"Received request at {const.GET_GRID_SPACING}")
    with open(const.METADATA_FILE, "r") as f:
        run_metadata = yaml.safe_load(f)
    # Get all unique grid spacing from the metadata file
    grid_spacing = {run["grid"] for run in run_metadata.values()}
    return flask.jsonify(sorted(list(grid_spacing)))


@server.app.route(const.GET_SCIENTIFIC_VERSION, methods=["GET"])
@cross_origin(expose_headers=["Content-Type", "Authorization"])
@utils.endpoint_exception_handling(server.app)
def get_scientific_version():
    """
    Gets the scientific version from the metadata yaml file
    """
    server.app.logger.info(f"Received request at {const.GET_SCIENTIFIC_VERSION}")
    with open(const.METADATA_FILE, "r") as f:
        run_metadata = yaml.safe_load(f)
    # Get all unique scientific version from the metadata file
    scientific_version = {str(run["scientific_version"]) for run in run_metadata.values()}
    return flask.jsonify(sorted(list(scientific_version)))


@server.app.route(const.GET_DATA_TYPES, methods=["GET"])
@cross_origin(expose_headers=["Content-Type", "Authorization"])
@utils.endpoint_exception_handling(server.app)
def get_data_types():
    """
    Gets the data types from the constants
    """
    server.app.logger.info(f"Received request at {const.GET_DATA_TYPES}")
    return flask.jsonify(const.AVAILABLE_DATA_TYPES)
