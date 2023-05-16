import flask
import yaml
from flask_cors import cross_origin

from cs_api import server, utils
from cs_api import constants as const
from dropbox_rclone import dropbox_reading


DEFAULT_CARD_INFO_KEYS = [
    "region",
    "tectonic_types",
    "grid",
    "scientific_version",
    "n_faults",
]


@server.app.route(const.GET_AVAILABLE_RUNS, methods=["GET"])
@cross_origin(expose_headers=["Content-Type", "Authorization"])
@utils.endpoint_exception_handling(server.app)
def get_available_runs():
    """
    Gets all the available runs on dropbox
    """
    server.app.logger.info(f"Received request at {const.GET_AVAILABLE_RUNS}")
    available_runs = dropbox_reading.find_available_runs()
    return flask.jsonify(available_runs)


@server.app.route(const.GET_RUN_INFO, methods=["GET"])
@cross_origin(expose_headers=["Content-Type", "Authorization"])
@utils.endpoint_exception_handling(server.app)
def get_full_run_info():
    """
    Gets all the run information from every run on dropbox
    and their metadata from the yaml file
    """
    server.app.logger.info(f"Received request at {const.GET_RUN_INFO}")
    (run,) = utils.get_check_keys(
        flask.request.args,
        ("run",),
    )
    run_info = dict()
    run_info[run] = dict()

    with open(const.METADATA_FILE, "r") as f:
        run_metadata = yaml.safe_load(f)

    # Get the info from the metadata file and fill the card info
    run_info[run]["card_info"] = dict()
    try:
        for metadata_key in run_metadata[run]:
            run_info[run]["card_info"][metadata_key] = run_metadata[run][metadata_key]
    except KeyError:
        # When the run name is not in the metadata yaml file set fields to Unknown
        for metadata_key in DEFAULT_CARD_INFO_KEYS:
            run_info[run]["card_info"][metadata_key] = "Unknown"

    # Get the info from the dropbox folder
    faults = dropbox_reading.get_run_info(run)
    run_info[run]["faults"] = faults
    run_info[run]["card_info"]["n_faults"] = len(faults)
    return flask.jsonify(run_info)
