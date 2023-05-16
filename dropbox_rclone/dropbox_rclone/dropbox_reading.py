import subprocess

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
