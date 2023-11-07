import argparse
from pathlib import Path
import subprocess
import os

import tarfile


# rclone ls dropbox:Cybershake/v22p12|grep -e "Source\|IM"| sed -E 's/^[[:space:]]+//' |cut -d" " -f2 |xargs -I {} rclone copy dropbox:Cybershake/v22p12/{} . --progress

DATA_TYPES = ["Source", "IM", "BB"]

TAR_ERROR_LOG = "tar_error.log"
TAR_OK_LOG = "tar_ok.log"


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
        "--no_download",
        help="If download has been already done, and wish to untar only",
        action="store_false",
        dest="ok_download",
    )

    parser.add_argument(
        "--inc_fault",
        help="Include this fault. All if unspecified.",
        action="append",
        default=[],
    )
    parser.add_argument(
        "--exc_fault",
        help="Exclude this fault. The fault is excluded if both inc_fault exc_fault are specified",
        action="append",
        default=[],
    )

    parser.add_argument(
        "--force_untar", help="Force untar from scratch", action="store_true"
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

    dropbox_path = f"dropbox:Cybershake/{dropbox_cs_ver}"

    p = subprocess.Popen(
        f"rclone lsd {dropbox_path}",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = p.communicate()
    out = out.decode("utf-8")
    err = err.decode("utf-8")

    assert "ERROR" not in err, f"CS version not found: {dropbox_cs_ver}"

    fault_names = [x.split(" ")[-1] for x in out.split("\n") if len(x) > 0]
    fault_names = [
        x for x in fault_names if not x.startswith("_")
    ]  # skip if the folder name starts with _

    if len(args.inc_fault) == 0:
        args.inc_fault = fault_names

    download_root.mkdir(exist_ok=True, parents=True)
    assert os.access(download_root, os.X_OK | os.W_OK)

    tar_error_log = download_root / TAR_ERROR_LOG
    tar_ok_log = download_root / TAR_OK_LOG

    if args.force_untar:  # enforce untar from scratch
        tar_ok_log.unlink(missing_ok=True)  # delete the ok log
        tar_error_log.unlink(missing_ok=True)  # delete the error log

    log_ok_list = []
    fault_to_skip_download = []
    if tar_ok_log.exists():
        with open(tar_ok_log, "r") as f:
            log_ok_list = f.read().split("\n")
        log_ok_list = [x for x in log_ok_list if len(x) > 0]

    log_error_list = []
    if tar_error_log.exists():
        with open(tar_error_log, "r") as f:
            log_error_list = f.read().split("\n")
        log_error_list = [x for x in log_error_list if len(x) > 0]

    # final list of faults to download.
    faults_to_include = list(set(args.inc_fault) - set(args.exc_fault))

    if args.ok_download:
        include_txt = ""
        for (
            fault_name
        ) in (
            faults_to_include
        ):  # previously downloaded tar,if still present, will be skipped
            for data_type in data_types:
                include_txt += f" --include {fault_name}_{data_type}*.tar"
        logfile = download_root / f"{dropbox_cs_ver}.log"
        print(
            f"## Downloading {dropbox_path} to {download_root}. Check progress with tail -f {logfile}"
        )
        cmd = f"rclone copy {dropbox_path} {download_root} {include_txt} --progress"
        print(cmd)
        with open(logfile, "w") as f:
            p = subprocess.Popen(cmd, shell=True, stdout=f, stderr=f)
            out, err = p.communicate()
        print(f"## Downloading {dropbox_path} completed")
        print(out)
        print(err)

    else:
        print(f"## Skipping download")

    print(f"## Extracting TAR files")
    print(download_root)
    tarfiles = list(download_root.glob("*/*.tar"))  # there may be old tar files
    tarfiles = sorted(tarfiles)
    failed_tar_count = 0
    print(tarfiles)
    for t in tarfiles:
        if t.name in log_ok_list:  # skip if old ones
            print(f"### Skip {t} as previously handled successfully")
            continue
        if t.name in log_error_list:
            print(f"### !!! Skip {t} is known to be broken")
            continue

        print(f"### Extracting {t}")
        fault_dir = t.parent
        chunks = t.name.split(".tar")[0].split("_")
        if len(chunks) == 2:  # single tar file
            fault_name, data_type = chunks
            num = None
        elif len(chunks) == 3:  # tar group
            fault_name, data_type, num = chunks
        else:
            continue
        if data_type not in data_types:
            continue

        if fault_name in args.exc_fault:
            print(f"### !!! Skip {fault_name} as specified")
            continue

        untar_dir = fault_dir / data_type
        untar_dir.mkdir(exist_ok=True, parents=True)
        try:
            # Extract the tar file
            p = subprocess.Popen(
                f"tar -xf {t} -C {untar_dir}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            p.wait()

            # Check to ensure the tar extracted files are the same as whats in the tar
            p = subprocess.Popen(
                f"tar --compare --file={t} {untar_dir}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            (
                err,
                _,
            ) = p.communicate()  # this command sends the error message to stdout.
            err = err.decode("utf-8")

            # Check there was no errors in the tar compare
            if len(err) > 0:
                print(f"### !!! {t} is broken")
                failed_tar_count += 1
                with open(tar_error_log, "a") as f:
                    f.write(f"{t.name}\n")
                continue
            else:
                print(f"### {t} is good")
                with open(tar_ok_log, "a") as f:
                    f.write(f"{t.name}\n")

        except Exception as e:
            print(f"### !!! {t} is broken")
            failed_tar_count += 1
            with open(tar_error_log, "a") as f:
                f.write(f"{t.name}\n")
            continue

        if cleanup:
            print(f" ### Deleting {t}")
            os.remove(t)

    if failed_tar_count > 0:
        print(
            f"### !!! {failed_tar_count} tar files are broken, read {tar_error_log} for details"
        )
    else:
        print(f"### All tar files are good")
