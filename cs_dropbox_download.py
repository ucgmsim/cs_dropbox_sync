import argparse
from pathlib import Path
import subprocess
import os

import tarfile



# rclone ls dropbox:Cybershake/v22p12|grep -e "Source\|IM"| sed -E 's/^[[:space:]]+//' |cut -d" " -f2 |xargs -I {} rclone copy dropbox:Cybershake/v22p12/{} . --progress

DATA_TYPES = ["Source", "IM", "BB"]

TAR_ERROR_LOG = "tar_error.log"

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
        help="Download directory. Current directory if not specified",
        type=Path,
        default="",
    )
    parser.add_argument(
        "--cleanup", help="Delete *.tar files after extraction", action="store_true"
    )

    parser.add_argument(
        "--no_download", help="If download has been already done, and wish to untar only", action="store_false", dest="ok_download")
    parser.add_argument(
        "--skip_fault", help="Skip processing this fault",
        action="append",
        default=[],
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
    download_root = args.download_dir.resolve() 
    cleanup = args.cleanup

    print(args.data_types)

    # TODO: check rclone

    dropbox_path = f"dropbox:Cybershake/{dropbox_cs_ver}"

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

    download_root.mkdir(exist_ok=True,parents=True)
    assert os.access(download_root, os.X_OK | os.W_OK)


    if args.ok_download:
        include_txt = ""
        for data_type in data_types:
            include_txt += f" --include *_{data_type}.tar"
        logfile = download_root/f"{dropbox_cs_ver}.log"
        print(f"## Downloading {dropbox_path} to {download_root}. Check progress with tail -f {logfile}")
        cmd = f"rclone copy {dropbox_path} {download_root} {include_txt} --progress"
        print(cmd)
        with open(logfile, "w") as f:
            p=subprocess.Popen(cmd, shell=True, stdout=f, stderr=f)
            out, err= p.communicate()
        print(f"## Downloading {dropbox_path} completed")
        print(out)
        print(err)

    else:
        print(f"## Skipping download")

    error_log = download_root / TAR_ERROR_LOG
    error_lst = []
    if error_log.exists():
        with open(error_log, "r") as f:
            error_list = f.read().split("\n")
        error_list = [x for x in error_list if len(x)>0] 
    
    print(f"## Extracting TAR files")
    print(download_root)
    tarfiles = list(download_root.glob("*/*.tar"))
    print(tarfiles)
    for t in tarfiles:

        if t.name in error_list:
            print(f"### !!! Skip {t} is known to be broken")
            continue

        print(f"### Extracting {t}")
        tar = tarfile.open(t, "r")
        fault_dir=t.parent
        chunks = t.name.split(".tar")[0].split("_")
        if len(chunks) == 2: # single tar file
            fault_name, data_type = chunks
            num = None
        elif len(chunks) ==3: #tar group
            fault_name, data_type, num = chunks
        else:
            continue
        if data_type not in data_types:
            continue

        if fault_name in args.skip_fault:
            print(f"### !!! Skip {fault_name} as specified")
            continue

        untar_dir=fault_dir/data_type
        untar_dir.mkdir(exist_ok=True,parents=True)
        try:
            tar.extractall(path=untar_dir)
        except EOFError:
            print(f"### CRITICAL {t} is broken")
            with open(error_log, "a") as f:
                f.write(f"{t.name}\n")
            continue
        if cleanup:
            print(f" ### Deleting {t}")
            os.remove(t)
