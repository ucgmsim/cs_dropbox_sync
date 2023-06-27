import flask
import yaml
from flask_cors import cross_origin

from cs_api import server, utils
from cs_api import constants as const
from cs_api.db import db


@server.app.route(const.GET_AVAILABLE_RUNS, methods=["GET"])
@cross_origin(expose_headers=["Content-Type", "Authorization"])
@utils.endpoint_exception_handling(server.app)
def get_available_runs():
    """
    Gets all the available runs on dropbox
    """
    server.app.logger.info(f"Received request at {const.GET_AVAILABLE_RUNS}")
    available_runs = db.get_available_run_names()
    return flask.jsonify(available_runs)


@server.app.route(const.GET_RUN_INFO, methods=["GET"])
@cross_origin(expose_headers=["Content-Type", "Authorization"])
@utils.endpoint_exception_handling(server.app)
def get_full_run_info():
    """
    Gets all the run information from every run on dropbox
    and their metadata from the db
    """
    server.app.logger.info(f"Received request at {const.GET_RUN_INFO}")
    run_infos = []
    available_runs = db.get_available_runs()
    for run in available_runs:
        run_info = dict()
        run_name = run.run_name
        run_info[run_name] = dict()

        # Add card info such as region, tectonic types, grid spacing, etc.
        run_info[run_name]["card_info"] = dict()
        run_info[run_name]["card_info"]["region"] = run.region
        run_info[run_name]["card_info"]["tectonic_types"] = sorted(
            [tect_type.tect_type for tect_type in run.tect_types]
        )
        run_info[run_name]["card_info"]["grid_spacing"] = run.grid_spacing.grid_spacing
        run_info[run_name]["card_info"]["scientific_version"] = run.scientific_version.scientific_version
        run_info[run_name]["card_info"]["n_faults"] = len(run.faults)

        # Add data types available such as BB, IM, Source
        run_info[run_name]["data_types"] = [data_type.data_type for data_type in run.data_types]

        # Add fault info such as fault name and associated files
        run_info[run_name]["faults"] = dict()
        for fault in run.faults:
            run_info[run_name]["faults"][fault.fault_name] = dict()
            for file in fault.files:
                # Add file info such as data type, file size, and download link
                run_info[run_name]["faults"][fault.fault_name][file.file_name] = dict()
                run_info[run_name]["faults"][fault.fault_name][file.file_name][
                    "data_type"
                ] = file.data_type.data_type
                run_info[run_name]["faults"][fault.fault_name][file.file_name][
                    "file_size"
                ] = file.file_size
                run_info[run_name]["faults"][fault.fault_name][file.file_name][
                    "download_link"
                ] = file.download_link
        run_infos.append(run_info)

    return flask.jsonify(run_infos)
