from cs_api.server import db

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


def get_run_types():
    """
    Get the run types aviailable from the database
    :return: list of different run types e.g. (Historical, Cybershake)
    """
    return sorted([run_type.type for run_type in RunType.query.all()])


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


def get_all_unique_faults():
    """
    Get all the unique faults from the database
    :return: list of unique faults
    """
    faults = Fault.query.all()
    unique_faults = {fault.fault_name for fault in faults}
    return sorted(list(unique_faults))


def get_all_unique_sites():
    """
    Get all the unique sites from the database
    :return: list of unique sites
    """
    sites = Site.query.all()
    unique_sites = {site.site_name for site in sites}
    return sorted(list(unique_sites))


def add_run(run: Run):
    """
    Add a run to the database
    :param run: run object
    :return: None
    """
    db.session.add(run)
    db.session.commit()
