import yaml

import pandas as pd

from cs_api.server import db
from cs_api import constants as const
from dropbox_rclone import dropbox_reading

# Because models need to be imported after db gets imported
from cs_api.db.models import *

DEFAULT_DATA_TYPES = ["BB", "IM", "Source"]
DEFAULT_RUN_TYPES = ["Cybershake", "Historical"]

# Load the Site df
site_df = pd.read_csv(const.SITE_DF_FILE, index_col=0)

# Load the dropbox df
dropbox_df = pd.read_csv(const.DROPBOX_FILE, index_col=0)

# Add db.drop_all() if you want to drop all tables and start from scratch
db.drop_all()

# Create tables - It only creates when tables don't exist
db.create_all()
db.session.commit()

# Read the yaml run_metadata file and insert data into the database
with open(const.METADATA_FILE, "r") as f:
    run_metadata = yaml.safe_load(f)

# Add the tectonic types to the database
tectonic_types = {
    tect_type for run in run_metadata.values() for tect_type in run["tectonic_types"]
}
for tect_type in tectonic_types:
    db.session.add(TectType(tect_type=tect_type))

# Add the grid spacings to the database
grid_spacings = {run["grid"] for run in run_metadata.values()}
for grid_spacing in grid_spacings:
    db.session.add(GridSpacing(grid_spacing=grid_spacing))

# Add the run types to the database
for run_type in DEFAULT_RUN_TYPES:
    db.session.add(RunType(type=run_type))

# Add the data types to the database
for data_type in DEFAULT_DATA_TYPES:
    db.session.add(DataType(data_type=data_type))


# Add the runs and all their fault information to the database
for run, run_info in run_metadata.items():
    print(f"Adding run {run} to the database")
    run_obj = Run(
        run_name=run, run_info=run_info, site_df=site_df, dropbox_df=dropbox_df
    )
    db.session.add(run_obj)

db.session.commit()
print("Finished adding runs to the database")
