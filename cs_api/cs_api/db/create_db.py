import yaml

from cs_api.server import db
from cs_api import constants as const
from dropbox_rclone import dropbox_reading

# Because models need to be imported after db gets imported
from cs_api.db.models import *

# Create tables - It only creates when tables don't exist
db.create_all()
db.session.commit()

# Read the yaml run_metadata file and insert data into the database
with open(const.METADATA_FILE, "r") as f:
    run_metadata = yaml.safe_load(f)
for run in run_metadata.values():
    faults = dropbox_reading.get_run_info(run)
    db.session.add(Run(run, len(faults), run["region"], run["grid"], run["scientific_version"], run["tectonic_types"]))
    db.session.commit()
