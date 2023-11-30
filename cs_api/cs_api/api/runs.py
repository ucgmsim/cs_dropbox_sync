import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

import flask
import pandas as pd
from flask_cors import cross_origin

from cs_api import server, utils
from cs_api import constants as const
from cs_api.db import db as cs_db
from cs_api.server import db
from cs_api.db.models import Run
from dropbox_rclone.dropbox_rclone.scripts.cs_dropbox_download import download


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
    available_runs = cs_db.get_available_runs()
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
        run_info[run_name]["card_info"]["run_type"] = run.type.type
        run_info[run_name]["card_info"]["n_faults"] = len(run.faults)

        # Add data types available such as BB, IM, Source
        run_info[run_name]["data_types"] = [
            data_type.data_type for data_type in run.data_types
        ]

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


@server.app.route(const.GET_RUNS_FROM_INTERESTS, methods=["GET"])
@cross_origin(expose_headers=["Content-Type", "Authorization"])
@utils.endpoint_exception_handling(server.app)
def get_runs_from_interests():
    """
    Gets all run names that contain the given interests of Sites or Sources
    """
    filter_by, filter_list = utils.get_check_keys(
        flask.request.args,
        ("filter_by", "filter_list"),
    )
    filter_list = filter_list.split(",")
    filtered_runs = []
    available_runs = cs_db.get_available_runs()
    for run in available_runs:
        if filter_by == "sources":
            for fault in run.faults:
                if fault.fault_name in filter_list:
                    filtered_runs.append(run.run_name)
                    break
        elif filter_by == "sites":
            for site in run.sites:
                if site.site_name in filter_list:
                    filtered_runs.append(run.run_name)
                    break
        else:
            raise ValueError(
                f"filter_by parameter must be either 'sources' or 'sites', not {filter_by}"
            )
    return flask.jsonify(filtered_runs)


@server.app.route(const.ADD_RUN, methods=["POST"])
@cross_origin(expose_headers=["Content-Type", "Authorization"])
@utils.endpoint_exception_handling(server.app)
def add_run():
    """
    Adds the run to the database
    """
    server.app.logger.info(f"Received request at {const.ADD_RUN}")
    (
        run_name,
        dropbox_folder,
        run_type,
        region,
        tectonic_types,
        grid_spacing,
        secret_key,
    ) = utils.get_check_keys(
        flask.request.args,
        (
            "run_name",
            "dropbox_folder",
            "run_type",
            "region",
            "tectonic_types",
            "grid_spacing",
            "secret_key",
        ),
    )
    tectonic_types = tectonic_types.split(",")

    # Check the secret key is correct
    if secret_key != os.environ["SECRET_KEY"]:
        return flask.jsonify({"error": "Incorrect secret key"}), 401
    else:
        dropbox_directory = f'dropbox:{"/".join(dropbox_folder.split("/")[2:])}'

        # Load the site_df by taking the current files path and navigating to the resouces directory
        site_df_ffp = Path(__file__).parent.parent / "db" / "resources" / "site_df.csv"
        site_df = pd.read_csv(site_df_ffp, index_col=0)
        # Create a new column for the current run and set all to False
        site_df[run_name] = False

        # Create a temporary directory to get the site information for the run
        temp_dir = TemporaryDirectory()
        temp_path = Path(temp_dir.name).resolve()

        # Download the IM data
        download(
            run_name,
            ["IM"],
            temp_path,
            dropbox_directory=dropbox_directory,
            cleanup=True,
            ok_download=True,
            force_untar=True,
        )

        # For each fault load the 1st realisation and get the list of stations
        for fault_dir in temp_path.iterdir():
            if fault_dir.is_dir():
                # Find the 1st realisation under any folder directory under fault_dir using glob
                rel_csv_ffp = list(fault_dir.glob("**/*REL01.csv"))[0]
                rel_csv = pd.read_csv(rel_csv_ffp)
                # Get the list of stations
                stations = rel_csv["station"].unique()
                # Set the stations to True
                site_df.loc[stations, run_name] = True

        # Clean up the temporary directory
        temp_dir.cleanup()

        # Create the run info from the given parameters
        run_info = {
            "region": region,
            "grid": grid_spacing,
            "tectonic_types": tectonic_types,
            "type": run_type,
        }

        # Create the run object
        run_obj = Run(run_name=run_name, run_info=run_info, site_df=site_df)
        db.session.add(run_obj)
        db.session.commit()

        return flask.jsonify({"success": "Correct secret key and added run to db"}), 200
