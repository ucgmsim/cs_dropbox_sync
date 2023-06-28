"""
Unsure if this is needed at all, might be replaced by admin login to add cybershake runs
"""
import yaml
import time
import logging

from pathlib import Path
import schedule

from cs_api.db import db, models
from cs_api import constants as const
from dropbox_rclone import dropbox_reading


def update_db(logger: logging.Logger):
    """
    This function performs the database update operation

    Parameters
    ---------
    logger: logging.Logger
        The logger object to log the database update messages
    """
    logger.info("Updating Database")

    # Find if there are any new runs
    available_runs = dropbox_reading.find_available_runs()
    db_runs = db.get_available_run_names()

    # If there are new runs, add them to the database
    if set(available_runs) != set(db_runs):
        logger.info("Found new runs")
        new_runs = set(available_runs) - set(db_runs)
        for run in new_runs:
            logger.info(f"Adding run {run}")
            # Add Unknown fields to the run_metadata yaml file
            with open(const.METADATA_FILE, "r") as f:
                run_metadata = yaml.safe_load(f)
            # Find the last run values for dictionary keys
            last_run_values = list(run_metadata.values())[-1]

            # Create a new set from the last runs keys
            run_info = {k: v for k, v in last_run_values.items()}
            # Set the region to Unknown and tectonic types to Shallow Crustal for a general guess
            run_info["region"] = "Unknown"
            run_info["tectonic_types"] = ["Shallow Crustal"]

            # Add the new run to the run_metadata dictionary
            run_metadata[run] = run_info

            # Write the modified data back to the YAML file
            with open(const.METADATA_FILE, 'w') as file:
                yaml.dump(run_metadata, file)

            run_obj = models.Run(run_name=run, run_info=run_info)
            db.add_run(run_obj)


def schedule_daily_update():
    """
    Schedule the daily update of the database
    Also run the update now
    """
    # Initialize logger
    logger = logging.getLogger('scanner')
    logger.setLevel(logging.INFO)

    # Create a file handler and set the log file name
    log_file = Path(__file__).parent.parent / "logs/scanner.log"
    file_handler = logging.FileHandler(log_file)

    # Create a log formatter and set the format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    # On call update the DB
    update_db(logger)

    # Schedule the update_db function to run every day at midnight
    schedule.every().day.at("00:00").do(update_db)

    # Run the pending scheduled tasks
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    schedule_daily_update()
