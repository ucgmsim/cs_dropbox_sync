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
# TODO Make this a function to be called by a scanner for new runs on dropbox
for run, run_info in run_metadata.items():
    print(f"Adding run {run} to the database")
    faults = dropbox_reading.get_run_info(run)
    run_obj = Run(
        run_name=run,
        n_faults=len(faults),
        region=run_info["region"],
        grid_spacing=GridSpacing.query.filter_by(grid_spacing=run_info["grid"]).first(),
        scientific_version=ScientificVersion.query.filter_by(
            scientific_version=str(run_info["scientific_version"])
        ).first(),
        tect_types=[
            TectType.query.filter_by(tect_type=tect_type).first()
            for tect_type in run_info["tectonic_types"]
        ],
    )
    # Create each fault for the run
    data_types_found = set()
    run_faults = []
    for fault, files in faults.items():
        fault_files = []
        for file_name, file_size in files.items():
            data_type_str = file_name.split(".")[0].split("_")[1]
            file_data_type = DataType.query.filter_by(data_type=data_type_str).first()
            data_types_found.add(file_data_type)
            file_obj = File(
                file_name=file_name.split("/")[1],
                download_link="",
                file_size=file_size,
                data_type=file_data_type,
            )
            fault_files.append(file_obj)
            db.session.add(file_obj)
        fault_obj = Fault(
            fault_name=fault,
            run=run_obj,
            files=fault_files,
        )
        run_faults.append(fault_obj)
        db.session.add(fault_obj)
    run_obj.data_types = list(data_types_found)
    run_obj.faults = run_faults
    db.session.add(run_obj)

db.session.commit()
print("Finished adding runs to the database")
