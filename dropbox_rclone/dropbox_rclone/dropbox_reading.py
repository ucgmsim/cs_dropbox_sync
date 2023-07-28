import os
import subprocess

import dropbox

from dropbox_rclone import contants as const


def find_available_runs():
    """
    Finds the available runs on dropbox and returns their names as a list
    """
    cmd = f"rclone lsf {const.CYBERSHAKE_DIRECTORY} --max-depth 1"
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out, err = p.communicate()
    runs = out.decode("utf-8").split("/\n")[:-1]
    # Ignore underscore runs
    runs = [run for run in runs if not run.startswith("_")]
    return runs


def get_run_info(run: str):
    """
    Gets the run info from the dropbox folder such as the
    Data types available and fault names and their file sizes per data type

    Parameters
    ----------
    run : str
        Name of the run

    Returns
    -------
    dict
        Dictionary of fault names and their files with sizes
    """
    cmd = f"rclone ls {const.CYBERSHAKE_DIRECTORY}/{run}"
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out, err = p.communicate()
    output = out.decode("utf-8").split("\n")[:-1]

    faults = dict()

    # Go through each output line and gather each fault name and the file size of each of the data types
    for line in output:
        # Strip extra spaces only on the start of the string
        line = line.lstrip()
        size, file = line.split(" ")
        # Ensure is a directory and does not start with an underscore
        if not file.startswith("_") and "/" in file:
            fault_name, tar = file.split("/")
            # Check if fault name is already in the dictionary
            if fault_name in faults:
                faults[fault_name][file] = size
            else:
                faults[fault_name] = {file: size}

    return faults


def get_download_link(file_path: str, dbx: dropbox.Dropbox):
    """
    Gets the download link for the file at the given path

    Parameters
    ---------
    file_path : str
        Path to the file on dropbox
    dbx : dropbox.Dropbox
        Dropbox object to use to get the download link

    Returns
    -------
    str
        Download link for the file
    """
    download_link = None
    try:
        # If no link was found, create a new one
        shared_link = dbx.sharing_create_shared_link_with_settings(file_path)
        download_link = shared_link.url.replace(
            "www.dropbox.com", "dl.dropboxusercontent.com"
        )
    except dropbox.exceptions.ApiError as e:
        shared_links = dbx.sharing_list_shared_links(file_path).links
        for link in shared_links:
            if link.path_lower == file_path.lower():
                download_link = link.url.replace(
                    "www.dropbox.com", "dl.dropboxusercontent.com"
                )
    if download_link is None:
        raise Exception("Could not find download link for file")
    return download_link


def get_dropbox_api_object():
    """
    Gets the dropbox object to use for the dropbox api

    Returns
    -------
    dropbox.Dropbox
        Dropbox object to use
    """
    key = os.environ["DROPBOX_KEY"]
    secret = os.environ["DROPBOX_SECRET"]
    refresh_token = os.environ["DROPBOX_REFRESH_TOKEN"]

    dbx = dropbox.Dropbox(app_key=key, app_secret=secret, oauth2_refresh_token=refresh_token)
    return dbx


def get_full_dropbox_path(run: str, file_name: str):
    """
    Gets the full path to the file on dropbox

    Parameters
    ----------
    run : str
        Name of the run e.g. v22p12
    file_name : str
        Name of the file e.g. Albury_IM.tar
    """
    return f"/{const.CYBERSHAKE_DIRECTORY.split(':')[-1]}/{run}/{file_name.split('_')[0]}/{file_name}"
