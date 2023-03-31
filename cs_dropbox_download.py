import argparse
from pathlib import Path
import subprocess
import os

import tarfile

# rclone ls dropbox:Cybershake/v22p12|grep -e "Source\|IM"| sed -E 's/^[[:space:]]+//' |cut -d" " -f2 |xargs -I {} rclone copy dropbox:Cybershake/v22p12/{} . --progress

DATA_TYPES = ["Source", "IM", "BB"]


def load_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("dropbox_cs_ver", type=str, help="CS ver stored in Dropbox")
    parser.add_argument(
        "-t",
        "--data_types",
        help="Data types to download. Gets all BB, IM, Source if not specified",
        action="append",
        choices=DATA_TYPES,
        default=[],
    )
    parser.add_argument(
        "--download_dir",
        help="Download directory. Current directory/{CS ver} if not specified",
        type=Path,
        default="",
    )
    parser.add_argument(
        "--cleanup", help="Delete *.tar files after extraction", action="store_true"
    )

    args = parser.parse_args()
    if args.data_types == []:
        args.data_types = DATA_TYPES

    if args.download_dir == "":
        args.download_dir = Path.cwd()

    return args


if __name__ == "__main__":
    args = load_args()

    dropbox_cs_ver = args.dropbox_cs_ver
    data_types = args.data_types
    download_root = args.download_dir.resolve() / dropbox_cs_ver
    cleanup = args.cleanup

    print(args.data_types)

    dropbox_path = f"dropbox:/Cybershake/{dropbox_cs_ver}"

    p = subprocess.Popen(
        f"rclone ls {dropbox_path}",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = p.communicate()
    out = out.decode("utf-8")
    err = err.decode("utf-8")

    assert "ERROR" not in err, f"CS version not found: {dropbox_cs_ver}"

    assert os.access(download_root, os.X_OK | os.W_OK)

    lines = out.split("\n")
    to_download = []
    for line in lines:
        try:
            size, filepath = line.split()
        except ValueError:
            continue
        fault_name, tar_file = filepath.split("/")
        try:
            data_type = tar_file.split(".tar")[0].split("_")[-1]
        except ValueError:
            continue
        if data_type not in data_types:
            continue
        else:
            # filepath, fault_name, tar_file, data_type all good
            if data_type in args.data_types:
                to_download.append((filepath, fault_name, data_type))

    print(f"## Download starting")

    #    for (filepath, fault_name, data_type) in to_download:
    #
    #        download_dir = download_root/fault_name/data_type
    #        download_dir.mkdir(parents=True, exist_ok=True)
    #        logfile = download_root/f"{Path(filepath).name}.log"
    #        print(f"### Downloading {filepath} to {download_dir}. Check progress with tail -f {logfile}")
    #        with open(logfile,"w") as f:
    #            p=subprocess.Popen(f"rclone copy {dropbox_path}/{filepath} {download_dir} --progress", shell=True, stdout=f, stderr=f)
    #            p.communicate()
    #        print(f"### Downloading {filepath} completed")

    print(f"## All Download is completed")

    print(f"## Extracting TAR files")
    tarfiles = list(download_root.glob("*/*/*.tar"))
    print(tarfiles)
    for t in tarfiles[:1]:
        print(f"### Extracting {t}")
        tar = tarfile.open(t, "r")
        tar.extractall(path=t.parent)
        if cleanup:
            print(f" ### Deleting {t}")
            os.remove(t)
