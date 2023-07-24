import yaml

from cs_api.server import db
from cs_api import constants as const
from dropbox_rclone import dropbox_reading

# Because models need to be imported after db gets imported
from cs_api.db.models import *

DEFAULT_DATA_TYPES = ["BB", "IM", "Source"]

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

# Add the scientific versions to the database
scientific_versions = {str(run["scientific_version"]) for run in run_metadata.values()}
for scientific_version in scientific_versions:
    db.session.add(ScientificVersion(scientific_version=scientific_version))

# Add the data types to the database
for data_type in DEFAULT_DATA_TYPES:
    db.session.add(DataType(data_type=data_type))


# Add the runs and all their fault information to the database
for run, run_info in run_metadata.items():
    print(f"Adding run {run} to the database")
    run_obj = Run(run_name=run, run_info=run_info)
    db.session.add(run_obj)

db.session.commit()
print("Finished adding runs to the database")
