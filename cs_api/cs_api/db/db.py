import yaml

from cs_api.server import db
from cs_api import constants as const
from dropbox_rclone import dropbox_reading

# Because models need to be imported after db gets imported
from cs_api.db.models import *


def get_data_types():
    """
    Get the data types from the database
    :return: list of data types
    """
    return [data_type.data_type for data_type in DataType.query.all()]


def get_tect_types():
    """
    Get the tectonic types from the database
    :return: list of tectonic types
    """
    return sorted([tect_type.tect_type for tect_type in TectType.query.all()])


def get_grid_spacings():
    """
    Get the grid spacings from the database
    :return: list of grid spacings
    """
    return sorted(
        [grid_spacing.grid_spacing for grid_spacing in GridSpacing.query.all()]
    )


def get_scientific_versions():
    """
    Get the scientific versions from the database
    :return: list of scientific versions
    """
    return sorted(
        [
            scientific_version.scientific_version
            for scientific_version in ScientificVersion.query.all()
        ]
    )


def get_available_run_names():
    """
    Get the available runs from the database
    :return: list of available runs
    """
    return [run.run_name for run in Run.query.all()]


def get_available_runs():
    """
    Get the available runs from the database
    :return: list of available run objects
    """
    return Run.query.all()
