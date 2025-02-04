import argparse
from pathlib import Path

import subprocess
import shutil
from typing import List, Dict, Tuple
import yaml

from dropbox_rclone import constants as const

FILE_PATTERN_CONF = "sync_patterns.yaml"
OPTIONAL_PATTERN_MARKER = "$"

FILES_TO_SYNC = "files_to_sync.yaml"
UPLOAD_REPORT = "progress.yaml"

DATA_TYPES = ["Source", "IM", "BB", "SAMPLE_BB"]

MAX_FILE_SIZE = 100 * 1073741824  # Maximum TAR file size


def load_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "cs_root", type=Path, help="Path to CS root", default=Path.cwd()
    )
    parser.add_argument(
        "files_to_sync",
        type=Path,
        help="YAML file keeping the list of files to sync",
        default=Path.cwd() / FILES_TO_SYNC,
    )
    parser.add_argument(
        "--tmp_dir",
        type=Path,
        help="Temp directory where files to be copied to and uploaded from",
        default=Path.cwd() / "tmp",
    )

    parser.add_argument(
        "-t",
        "--data_types",
        help="Data types to download. Gets all BB, IM, Source if not specified",
        action="append",
        choices=DATA_TYPES,
        default=[],
    )
    parser.add_argument(
        "-f",
        "--overwrite",
        action="store_true",
        help="Force uploading even if it has been previously uploaded",
    )

    parser.add_argument(
        "--no_checksum",
        action="store_false",
        dest="do_checksum",
        help="Skip rclone check after uploading",
    )

    args = parser.parse_args()
    if args.data_types == []:
        args.data_types = DATA_TYPES

    return args


def check_rclone() -> None:
    """
    Check if rclone is installed
    """
    p = subprocess.Popen(
        "which rclone", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out, err = p.communicate()
    assert len(err.decode("utf-8")) == 0, "rclone is not found"


def retrieve_dropbox_files(
    dropbox_link: Path, check_tar: bool = False, debug: bool = True
) -> List[str]:
    """
    Retrieve file names from the dropbox directory

    Parameters
    ----------
    dropbox_link:  Path
        Path to the dropbox directory. eg. dropbox:/QuakeCoRE/Public/Cybershake/v24p8
    check_tar: bool
        If True, check if the TAR files satisfying the correct naming scheme and collect them only
        Naming should be {fault_name}_{data_type}_{num}.tar or {fault_name}_{data_type}.tar
    debug: bool
        If True, print the file names found
    Returns
    -------
    List[str]
        list of file names found

    """
    # check_tar = True enforces collection of "desirable" TAR files only

    files_found = []
    cmd = f"rclone ls {dropbox_link}"
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out, err = p.communicate()
    lines = out.decode("utf-8").split("\n")
    for line in lines:
        try:
            _, filepath = line.split()  # returns size, filepath
        except ValueError:
            continue
        filename = Path(filepath).name  # just focus on the file name
        if check_tar:
            try:
                chunks = filename.split(".tar")[0].split(
                    "_"
                )  # eg. FiordSZ03_BB.tar, FiordSZ03_BB_1.tar
            except ValueError:
                continue
            if len(chunks) > 1:  # should be either 2 or 3
                pass
            else:  # not a file we are after, skip
                continue
        if debug:
            print(f" --{filename}")
        files_found.append(filename)

    return files_found


def copy_files(fault_name: str, data_type: str, work_dir: Path) -> bool:
    """
    Copy files from the source to the work directory

    Parameters
    ----------
    fault_name: str
        Fault name
    data_type: str
        Data type to copy. Can be BB, IM, Source, SAMPLE_BB
    work_dir: Path
        Working directory to copy files to

    Returns
    -------
    bool
        True if all files are copied successfully, False otherwise


    """
    all_good = True

    # chery_pick files and copy to work directory
    print(
        f"#### Copy {fault_name} {data_type} files to {work_dir.relative_to(Path.cwd())}"
    )
    files_to_copy = files_dict[fault_name][data_type].keys()
    work_dir.mkdir(parents=True, exist_ok=True)
    for f in files_to_copy:
        original_path = Path(f)
        if data_type == "BB" or data_type == "SAMPLE_BB":
            to_name = f"{original_path.parents[2].name}_{original_path.name}"  # eg BB.bin -> Dunstan_REL01_BB.bin
        else:
            to_name = original_path.name
        #        print(f"{f} is copied to {work_dir/to_name}")
        try:
            dest = shutil.copyfile(original_path, work_dir / to_name)
        except shutil.SameFileError:
            pass
        except PermissionError:
            print("Permission denied")
            all_good = False
        except:
            print(f"Error occurred while copying {original_path} to {work_dir}")
            all_good = False
        else:
            if Path(dest).stat().st_size != files_dict[fault_name][data_type][f]:
                print(f"File size differs after copying {original_path} to {work_dir}")
                all_good = False
            else:
                #                print(f"Good...File size identical after copying {original_path} to {work_dir}")
                pass
    assert all_good, f"Cherry-pick and copy filed for {fault_name} {data_type}"

    return all_good


class TARGroup:
    """
    Used to handle a group of TAR files when files to be archived need to be partitioned due to upload size limit

    If a tar file, such as AlpineK2T_BB.tar is going to be larger than size limit (100Gb currently), we will partition files
    such that the resulting tar files are below the size limit.
    As a result, we have AlpineK2T_BB_0.tar, AlpineK2T_BB_2.tar ..., with the last one ending with "f", such as AlpineK2T_BB_3f.tar
    This way, we know we have a complete set of TAR files if we find all 0, 1 ..3 labeled files with the AlpineK2T_BB prefix.
    """

    def __init__(self):
        self.found_partitions = []
        self.size = None  # number of partitions, initially unknown

    def get_size(self) -> int:
        return self.size

    def is_size_known(self) -> bool:
        """
        Check if the size of the TAR group is known
        Returns
        -------
        bool
            True if the size is known, False otherwise
        """
        return self.size is not None

    def found(self, num: str) -> None:
        """
        Report that a partition has been found
        Parameters
        ----------
        num : str
            The partition number found. Ends with "f" if it is the last partition
            eg. num=1, 2, 3f when AlpineK2T_BB_3f.tar is the last partition

        Returns
        -------
        None
        """
        if num.endswith("f"):  # The last partition ends with "f"
            num = int(num.strip("f"))
            self.size = num + 1
        else:
            num = int(num)

        self.found_partitions.append(num)

    def all_found(self) -> bool:
        """
        Check if all partitions have been found
        Returns
        -------
        bool
            True if all partitions have been found, False otherwise
        """
        return self.size == len(self.found_partitions)


def __make_partition(all_files: List[Path]) -> List[List[Path]]:
    """
    Make partitions of files if the total size exceeds the limit

    Parameters
    ----------
    all_files:  List[Path]
        List of files to partition

    Returns
    -------
    List[List[Path]]
        List of partitions of files

    """
    partition_list = []
    if len(all_files) == 0:
        print(
            f" WARNING: Files are empty. Consider -t argument (eg. -t BB) if you wish to upload without this data type"
        )
        return [[]]  # return an empty list as a partition

    one_partition = [all_files[0]]

    partition_size = all_files[0].stat().st_size

    for f in all_files[1:]:
        if partition_size + f.stat().st_size <= MAX_FILE_SIZE:
            one_partition.append(f)
            partition_size += f.stat().st_size
        else:  # including this will exceed. Finalize the current subset, start a new one
            # TODO: Currently f is assumed to be smaller than the size limit. Fix this if this assumption is not valid
            partition_list.append(one_partition)
            partition_size = f.stat().st_size
            one_partition = [f]

    if one_partition:  # last partition
        partition_list.append(one_partition)
    return partition_list


def pack(fault_name: str, data_type: str) -> bool:
    """
    Pack files into TAR files

    Parameters
    ----------
    fault_name: str
        Fault name
    data_type:  str
        Data type to pack. Can be BB, IM, Source, SAMPLE_BB

    Returns
    -------
    bool
        True if all files are packed successfully, False otherwise
    """

    work_dir = to_pack_root / fault_name / data_type
    tarfile_prefix = f"{fault_name}_{data_type}"

    to_upload_dir = to_upload_root / fault_name

    tarfile_prefix_inc_path = to_upload_root / fault_name / tarfile_prefix

    if (
        data_type == "SAMPLE_BB"
    ):  # SAMPLE_BB is a single file, not packed into a TAR file
        return copy_files(
            fault_name, data_type, to_upload_dir
        )  # no need to make a tar file

    all_good = copy_files(fault_name, data_type, work_dir)

    if (
        data_type == "Source"
    ):  # if "Source" is specified, we also need to look after "VM"
        all_good = all_good and copy_files(fault_name, "VM", work_dir)

    all_files = sorted(list(work_dir.glob("*")))

    partition_list = __make_partition(
        all_files
    )  # make partitions if total file size exceeds limit

    if len(partition_list) == 1:  # single TAR file
        if len(partition_list[0]) == 0:
            return False  # nothing to pack. Skip the rest of this function

        tar_files = [Path(f"{tarfile_prefix_inc_path}.tar")]
    else:
        print(f"#### TAR file too large. Made {len(partition_list)} partitions")
        tar_files = []
        for i in range(len(partition_list)):
            if i == len(partition_list) - 1:
                num = f"{i}f"  # the last TAR file ends with "f" for completeness test, eg. HikHBaymax_BBi_3f.tar
            else:
                num = i
            tar_files.append(Path(f"{tarfile_prefix_inc_path}_{num}.tar"))

    for tf in tar_files:
        if tf.exists():
            print(f"#### Deleting existing {tf}")
            tf.unlink()

    for i, one_partition in enumerate(partition_list):
        files_str = " ".join([str(f.relative_to(work_dir)) for f in one_partition])
        print(f"#### Making {tar_files[i].relative_to(Path.cwd())}")
        # make tar file
        # We are not using python 'tarfile' package due to limitations
        # We are going into work_dir, so that files to add to tar file will have their basenames when untarred.
        cmd = f"tar cvf {tar_files[i]} {files_str}"
        print(cmd)

        p = subprocess.Popen(
            cmd,
            cwd=str(work_dir),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        p.communicate()  # no returned value required here

        p = subprocess.Popen(
            f"tar --compare --file={tar_files[i]} {files_str}",
            cwd=str(work_dir),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        (
            err,
            _,
        ) = p.communicate()  # this command sends the error message to stdout.
        err = err.decode("utf-8")
        assert (
            len(err) == 0
        ), f"!!!! CRITICAL: tar failed\n {err}"  # tar was not successful - this can be bad, eg. storage full etc. let's just exit here.

        # remove files that have been successfully packed.
        p = subprocess.Popen(
            f"rm {files_str}",
            cwd=str(work_dir),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        p.communicate()  # no output expected

    # TODO: We may need to re-think "all_good". if True, only means file copy was good - as we abort if tar failed.
    return all_good


def upload(
    fault_name: str,
    do_checksum: bool = True,
) -> Tuple[bool, List[str]]:
    """
    Upload files to Dropbox

    Parameters
    ----------
    fault_name: str
        Fault name
    do_checksum: bool, default=True
        If True, check if the files are uploaded correctly by comparing checksums

    Returns
    -------
    Tuple[bool, List[str]]
        True if the files are uploaded successfully, False otherwise
        List of files uploaded

    """
    # Just upload everything from this fault_name's to_upload directory.
    # rclone uploads multiple files from the directory in parallel, maximising upload traffic
    dropbox_dir = f"{dropbox_path}/{fault_name}"
    p = subprocess.Popen(
        f"rclone mkdir {dropbox_dir}", shell=True, stdout=subprocess.PIPE
    )
    p.communicate()

    filename_pat = f"{fault_name}_*"  # {fault_name}_IM.tar {fault_name}_Source.tar {fault_name}_BB.tar {fault_name}_BB.bin/{fault_name}_REL01_BB.bin
    to_upload_dir = to_upload_root / fault_name
    files_to_upload = [f.name for f in list(to_upload_dir.glob(filename_pat))]

    # rclone copy {src} {dest}
    # 1. {src} is a file, and {dest} is a file, trivial
    # 2. {src} is a file, {dest} is a directory, the file will be placed under {dest}
    # 3. {src} is a directory, {dest} is a directory, all files under {src} will be copied to {dest}. No directory made
    # 4. {src} is a directory, {dest} is a file, error.

    progress_file = to_upload_root / f"{fault_name}_progress.log"
    check_file = to_upload_root / f"{fault_name}_check.log"

    print(f"#### Uploading {to_upload_dir.relative_to(Path.cwd())} to {dropbox_dir}.")
    print(f"\n\n --------   Check progress with     tail -f {str(progress_file)}\n\n")
    with open(progress_file, "w") as f:
        # can use rclone copy --checksum, but automatic size, modtime check is considered adequate.
        # https://forum.rclone.org/t/rclone-copy-files-and-checksum/14895/2 .
        # Besides, error (if any) collection via --checksum is not simple.
        # We will be using a separate rclone check below
        p = subprocess.Popen(
            f"rclone --progress copy {to_upload_dir} {dropbox_dir}",
            shell=True,
            stdout=f,
            stderr=f,
        )
        p.communicate()
        print(f"#### Uploading {to_upload_dir.relative_to(Path.cwd())} completed")

    files_found = retrieve_dropbox_files(dropbox_dir, check_tar=True)

    # Extra verification. Checks one-way only. ie. source files must exist on remote
    # and difference (if any) is logged in check_file. Use --no_checksum argument if too slow
    if do_checksum:
        p = subprocess.Popen(
            f"rclone check {to_upload_dir} {dropbox_dir} --one-way --differ {check_file}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        _, err = p.communicate()  # this command sends all output good or bad to stderr

        with open(check_file, "r") as f:
            diff_result = f.read()

        upload_success = len(diff_result) == 0
    else:
        # just check if the files are found in Dropbox. Might be adequate
        upload_success = len(set(files_to_upload) - set(files_found)) == 0

    if upload_success:
        print(
            f"#### Upload successful - deleting tmp dir {to_upload_dir.relative_to(Path.cwd())}"
        )
        shutil.rmtree(to_upload_dir)
    else:
        print(f"#### ERROR: Upload failed")
        print(err.decode("utf-8"))

    return upload_success, files_found


def mark_uploaded(
    fault_name: str, data_type: str, uploaded_files_dict: Dict, log: bool = True
) -> None:
    """
    Mark the specified data type has been uploaded for the given fault name.
    uploaded_files_dict[fault_name]=[BB,IM] means BB and IM data have been uploaded for fault_name

    Parameters
    ----------
    fault_name : str
        Fault name
    data_type: str
        Data type. Can be BB, IM, Source, SAMPLE_BB

    uploaded_files_dict: Dict
        Dictionary to keep track of uploaded data_type for a given fault_name
    log: bool, default=True
        If True, write the updated dictionary to a file
    Returns
    -------
    None
    """
    if data_type is None:
        uploaded_files_dict[fault_name] = []  # initislizing an empty list
    else:
        if data_type not in uploaded_files_dict[fault_name]:
            uploaded_files_dict[fault_name].append(data_type)
    report_path = work_root / f"{fault_name}_{UPLOAD_REPORT}"

    if log:
        with open(report_path, "w") as f:
            yaml.dump(uploaded_files_dict[fault_name], f)


def update_uploaded_status(
    tar_files: List[str],
    uploaded_files_dict: Dict,
    log: bool = True,
    debug: bool = True,
) -> None:
    """
    Update the uploaded status of the files

    Parameters
    ----------
    tar_files: List[str]
        List of TAR files found in the dropbox directory
    uploaded_files_dict
        Dictionary to keep track of uploaded files
    log : bool, default=True
        If True, write the updated dictionary to a file
    debug: bool, default=True
        If True, print debug information

    Returns
    -------
    None

    """
    tar_group = {}
    for tar_file in tar_files:
        try:
            chunks = tar_file.split(".tar")[0].split("_")
        except ValueError:
            continue

        if chunks[-1] == "BB.bin":
            fault_name = chunks[0]
            data_type = "SAMPLE_BB"
            num = None  # this is a sample BB (median or REL01), not a tar file
        else:
            if len(chunks) == 2:  # single tar file
                fault_name, data_type = chunks
                num = None

            elif len(chunks) == 3:  # this belongs to a tar group
                fault_name, data_type, num = chunks
            else:
                # this is not in the format we want, pass
                continue
        if fault_name not in fault_names:
            continue  # unknown fault_name
        if data_type not in DATA_TYPES:
            continue  # unknown type
        else:
            #           print(f"{fault_name} {data_type} {size}")
            if num is None:  # single tar file
                # easy, this has been uploaded.
                mark_uploaded(fault_name, data_type, uploaded_files_dict, log=log)

            else:  # tar group is considered fully uploaded if below satisfies
                #                print(f"{fault_name} {data_type} has tar_group")
                if (fault_name, data_type) not in tar_group:
                    # this is an unknown tar group. Create one and start tracking
                    tar_group[(fault_name, data_type)] = TARGroup()
                this_tar_group = tar_group[
                    (fault_name, data_type)
                ]  # retrieve a relevant tar group
                this_tar_group.found(num)  # report "num"-th partition has been found
                if this_tar_group.all_found() and debug:
                    print(f"{fault_name} {data_type} all partitions confirmed uploaded")
                mark_uploaded(fault_name, data_type, uploaded_files_dict, log=log)


if __name__ == "__main__":
    args = load_args()

    global cs_root, work_root, to_pack_root, to_upload_root, dropbox_path, fpconf, files_to_sync, data_types, fault_names

    cs_root = args.cs_root.resolve()
    files_to_sync = args.files_to_sync.resolve()
    tmp_dir = args.tmp_dir.resolve()
    data_types = args.data_types
    overwrite = args.overwrite
    do_checksum = args.do_checksum

    assert cs_root.exists()
    assert files_to_sync.exists()
    assert files_to_sync.exists()

    check_rclone()

    tmp_dir.mkdir(exist_ok=True, parents=True)

    cs_ver = cs_root.name

    work_root = tmp_dir / f"{cs_ver}"
    to_pack_root = work_root / "to_pack"
    to_upload_root = work_root / "to_upload"

    work_root.mkdir(parents=True, exist_ok=True)
    to_pack_root.mkdir(exist_ok=True)
    to_upload_root.mkdir(exist_ok=True)

    dropbox_path = f"{const.CYBERSHAKE_DIRECTORY}/{cs_ver}"

    with open(files_to_sync, "r") as f:
        files_dict = yaml.safe_load(f)

    fault_names = sorted(files_dict.keys())
    if "." in fault_names:
        fault_names.remove(".")  # remove "." from the fault_names list.
        print(f"#### Uploading misc files from root")
        for misc_file in list(files_dict["."].keys()):
            p = subprocess.Popen(
                f"rclone --progress copy {misc_file} {dropbox_path}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            p.communicate()

    uploaded_files = {}
    for fault_name in fault_names:
        mark_uploaded(fault_name, None, uploaded_files)  # initializing uploaded_files

    print(f"#### Files in {dropbox_path}")
    tar_files = retrieve_dropbox_files(
        dropbox_path
    )  # may contain non-tar files or tar files not in the desired format. Will be filtered out by the next step
    update_uploaded_status(tar_files, uploaded_files)

    print(f"#### Files already uploaded at {dropbox_path}")
    print(uploaded_files)

    for fault_name in fault_names:
        print("\n\n-------------------------------")
        print(f"        {fault_name}")
        print("\n-------------------------------\n\n")

        # packing all data_types
        pack_ok = {}.fromkeys(data_types)
        to_upload_dir = to_upload_root / fault_name
        if to_upload_dir.exists():
            print(
                f"#### Info: {to_upload_dir.relative_to(Path.cwd())} already exists. Delete"
            )
            shutil.rmtree(to_upload_dir)

        to_upload_dir.mkdir(parents=True, exist_ok=True)
        for data_type in data_types:

            if overwrite or (
                data_type not in uploaded_files[fault_name]
            ):  # skip already uploaded file unless overwrite enforced
                if overwrite and data_type in uploaded_files[fault_name]:
                    print(
                        f"#### Warning: Existing {fault_name} {data_type} will be overwritten"
                    )
                pack_ok[data_type] = pack(fault_name, data_type)
                if not pack_ok[data_type]:
                    print(
                        f"#### {fault_name} {data_type} packing failed - Upload skipped"
                    )
                    continue

        # if any TAR files have been produced for upload, go ahead
        if any(pack_ok.values()):
            upload_ok, tar_files_uploaded = upload(fault_name, do_checksum)
            assert upload_ok, "!!!! CRITICAL: Upload failed for {fault_name}"

            update_uploaded_status(tar_files_uploaded, uploaded_files)

    print(f"#### Upload finished. Verification begins")

    error_count = 0
    for fault_name in fault_names:
        for data_type in data_types:
            if data_type not in uploaded_files[fault_name]:
                print(f"!!! {fault_name} : {data_type}  had an uploading issue")
                error_count += 1

    # verify if the files uploaded are truly found on Dropbox
    tar_files_found = retrieve_dropbox_files(dropbox_path, check_tar=True, debug=False)
    retrieved_files = {}
    for fault_name in fault_names:
        mark_uploaded(fault_name, None, retrieved_files)  # initializing retrieved_files

    update_uploaded_status(tar_files_found, retrieved_files, log=False, debug=False)
    for fault_name in fault_names:
        for dt in uploaded_files[fault_name]:  # IM, BB, Source
            if dt not in retrieved_files[fault_name]:
                print(
                    f"!!! {fault_name} : {data_type} supposedly uploaded, but not found online"
                )
                error_count += 1

    print(f"#### Completed")
    print(f"   Errors: {error_count}")
