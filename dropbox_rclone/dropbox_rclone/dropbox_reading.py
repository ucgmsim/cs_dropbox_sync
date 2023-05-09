from pathlib import Path

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
    return out.decode("utf-8").split("/\n")
