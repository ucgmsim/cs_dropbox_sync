import argparse
import os
from pathlib import Path
from multiprocessing import Pool

import subprocess
import shutil
import yaml



FILE_PATTERN_CONF="sync_patterns.yaml"
OPTIONAL_PATTERN_MARKER="$"

FILES_TO_SYNC="files_to_sync.yaml"
UPLOAD_REPORT="progress.yaml"

DATA_TYPES=['Source','IM','BB']

MAX_FILE_SIZE = 100*1073741824

def load_args():
    parser= argparse.ArgumentParser()
    parser.add_argument(
        "cs_root",type=Path, help="Path to CS root", default=Path.cwd()
    )
    parser.add_argument(
        "files_to_sync",type=Path, help="YAML file keeping the list of files to sync", default=Path.cwd()/FILES_TO_SYNC)
    parser.add_argument(
        "tmp_dir",type=Path, help="Temp directory where files to be copied to and uploaded from", default="/tmp")
    parser.add_argument(
        "--nproc",type=int, help="Number of concurrent processes", default=2)

    parser.add_argument(
        '-t', "--data_types", help="Data types to download. Gets all BB, IM, Source if not specified",action='append', choices=DATA_TYPES, default=[])


    args = parser.parse_args()
    if args.data_types == []:
        args.data_types = DATA_TYPES

    return args

def copy_files(fault_name, data_type, work_dir):
    all_good=True

    # chery_pick files and copy to work directory
    print(f"#### Copy {fault_name} {data_type} files to {work_dir}")
    files_to_copy = files_dict[fault_name][data_type].keys()
    work_dir.mkdir(parents=True, exist_ok=True)
    for f in files_to_copy:
        original_path = Path(f)
        if data_type == 'BB':
            to_name=f"{original_path.parents[2].name}_{original_path.name}" #eg BB.bin -> Dunstan_REL01_BB.bin
        else:
            to_name=original_path.name
   #        print(f"{f} is copied to {work_dir/to_name}")
        try:
            dest=shutil.copyfile(original_path,work_dir/to_name)
        except shutil.SameFileError:
            pass
        except PermissionError:
            print("Permission denied")
            all_good=False
        except:
            print(f"Error occurred while copying {original_path} to {work_dir}")
            all_good=False
        else:
            if Path(dest).stat().st_size != files_dict[fault_name][data_type][f]:
                print(f"File size differs after copying {original_path} to {work_dir}")
                all_good=False
            else:
#                print(f"Good...File size identical after copying {original_path} to {work_dir}")
                pass
    assert all_good, f"Cherry-pick and copy filed for {fault_name} {data_type}"

    return all_good

def __make_partition(all_files):
    partition_list=[]
    one_partition=[all_files[0]]
    partition_size = all_files[0].stat().st_size

    for f in all_files[1:]:
        if partition_size + f.stat().st_size <= MAX_FILE_SIZE:
            one_partition.append(f)
            partition_size += f.stat().st_size
        else: # including this will exceed. Finalize the current subset, start a new one
            #TODO: f is assumned to be smaller than the size limit
            partition_list.append(one_partition)
            print(one_partition)
            print(partition_size)
            partition_size = f.stat().st_size
            one_partition = [f]

    if one_partition: # last partition
        partition_list.append(one_partition)
        print(one_partition)
        print(partition_size)
    return partition_list


def pack(fault_name, data_type):

    work_dir=to_pack_root/fault_name/data_type        
    tarfile_prefix=f"{fault_name}_{data_type}"

    to_upload_dir = to_upload_root / fault_name
    to_upload_dir.mkdir(parents=True,exist_ok=True)

    tarfile_prefix_inc_path=to_upload_root/fault_name/tarfile_prefix

    all_good = copy_files(fault_name, data_type, work_dir)
    if data_type == "Source":
        all_good = all_good and copy_files(fault_name, "VM", work_dir)


    all_files = sorted(list(work_dir.glob("*")))


    partition_list = __make_partition(all_files)

    if len(partition_list) == 1: #single TAR file
        tar_files = [Path(f"{tarfile_prefix_inc_path}.tar")] 
    else:
        print(f"#### TAR file too large. Making {len(partition_list)} partitions")
        tar_files = []
        for i in range(len(partition_list)):
            if i == len(partition_list)-1:
                num = f"{i}f" # the last TAR file ends with "f", eg. HikHBaymax_BBi_3f.tar
            else:
                num = i
            tar_files.append(Path(f"{tarfile_prefix_inc_path}_{num}.tar"))

    for tf in tar_files:
        if tf.exists():
            print(f"#### Deleting existing {tf}")
            tf.unlink() 


    for i, one_partition in enumerate(partition_list):
        #we are going into work_dir, tar file will be in its parent (ie. ../work_dir)
        
        files_str=" ".join([str(f.relative_to(work_dir)) for f in one_partition])
        print(f"#### Making {tar_files[i]}")
        # make tar file - not using tarfile package to avoid full-path when extracted
        cmd = f"tar cvf {tar_files[i]} {files_str}"
        print(cmd)
        p=subprocess.Popen(cmd,cwd=str(work_dir),shell=True, stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err=p.communicate()
        print(out)
        print(err)
    
    return all_good

def retrieve_dropbox_files(dropbox_link, check_tar=False):
    files_found = []
    p=subprocess.Popen(f"rclone ls {dropbox_link}",shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out,err=p.communicate()
    lines=out.decode('utf-8').split("\n")
    for line in lines:
        try:
            _, filepath = line.split()
        except ValueError:
            continue
        a_file = Path(filepath).name
        if check_tar:
            try:
                chunks = a_file.split(".tar")[0].split("_")
            except ValueError:
                continue
            if len(chunks) >1:
                pass
            else: # not a file we are after, skip
                continue
        print(a_file)
        files_found.append(a_file)

    return files_found
 
def upload(fault_name): # doesn't care about data types. Just upload everything in the directory
    dropbox_dir = f"{dropbox_path}/{fault_name}"
    p=subprocess.Popen(f"rclone mkdir {dropbox_dir}",shell=True,stdout=subprocess.PIPE)
    p.communicate()

    tar_file=f"{fault_name}_*.tar" #may be multiple
    to_upload_dir = to_upload_root/fault_name
    tar_files_to_upload = [tf.name for tf in list(to_upload_dir.glob(tar_file))]

    all_good = True
   
    # rclone copy {src} dropbox:{dest}
    # 1. {src} is a file, and {dest} is a file, trivial
    # 2. {src} is a file, {dest} is a directory, the file will be placed under {dest}
    # 3. {src} is a directory, {dest} is a directory, all files under {src} will be copied to {dest}. No directory made
    # 4. {src} is a directory, {dest} is a file, error.
    logfile = to_upload_root/f"{fault_name}_progress.log"
    print(f"#### Uploading {to_upload_dir} to {dropbox_dir}. Check progress with tail -f {str(logfile)}")
    with open(logfile,"w") as f:
        p=subprocess.Popen(f"rclone --progress copy {to_upload_dir} {dropbox_dir}",shell=True,stdout=f, stderr=f)
        p.communicate()
        print(f"#### Uploading {to_upload_dir} completed")

    tar_files_found = retrieve_dropbox_files(dropbox_dir, check_tar=True)

    if len(set(tar_files_to_upload) - set(tar_files_found)) > 0:
        all_good = False
   

    return all_good, tar_files_found

class partition:
    def __init__(self):
        self.found_partitions=[]
        self.size = None

    def get_size(self):
        return self.size

    def is_size_known(self):
        return self.size is not None
    
    def found(self, num):
        if num.endswith("f"): #last num
            num=int(num.strip("f"))
            self.size = num+1
        else:
            num=int(num)

        self.found_partitions.append(num)

    def all_found(self):
        return self.size == len(self.found_partitions)
        

def update_uploaded(fault_name,data_type):
    if data_type == []:
        uploaded[fault_name]=[]
    else:
        if data_type not in uploaded[fault_name]:
            uploaded[fault_name].append(data_type)
    print(f"write to {work_root}/{fault_name}_{UPLOAD_REPORT}")

    with open(work_root/f"{fault_name}_{UPLOAD_REPORT}","w") as f:
        yaml.dump(uploaded[fault_name],f)

def check_uploaded_tar_files(tar_files):
    partitions={}
    for tar_file in tar_files:
        try:
            chunks = tar_file.split(".tar")[0].split("_")
        except ValueError:  
            continue
        if len(chunks)==2:
            fault_name, data_type = chunks
            num = None
        elif len(chunks)==3:
            fault_name, data_type, num = chunks
        else:
            #this is not in the format we want, pass
            continue
        if data_type not in DATA_TYPES:  
            continue # unknown type
        else:    
#           print(f"{fault_name} {data_type} {size}")
    #        uploaded[fault_name].append(data_type)
            if num is None:
                #easy, this has been uploaded.
                update_uploaded(fault_name,data_type)

            else: #considered true when 
                print(f"{fault_name} {data_type} has partitions")
                if (fault_name, data_type) not in partitions:
                    partitions[(fault_name,data_type)]=partition()
                this_partition = partitions[(fault_name,data_type)]
                this_partition.found(num)
                if this_partition.all_found():
                    print(f"{fault_name} {data_type} uploaded all partitions")
                    update_uploaded(fault_name,data_type)


if __name__ == "__main__":
    args = load_args()

    global cs_root,work_root, to_pack_root, to_upload_root, dropbox_path,fpconf,files_to_sync, uploaded, data_types


    cs_root = args.cs_root
    files_to_sync = args.files_to_sync
    tmp_dir = args.tmp_dir
    data_types = args.data_types

    nproc = args.nproc

    assert cs_root.exists()
    assert files_to_sync.exists()
    assert os.access(tmp_dir, os.X_OK | os.W_OK) # check if writing to tmp_dir is ok

    cs_ver = cs_root.name

    work_root = tmp_dir/f"{cs_ver}"
    to_pack_root = work_root / "to_pack"
    to_upload_root = work_root / "to_upload"
    
    work_root.mkdir(parents=True, exist_ok=True)
    to_pack_root.mkdir(exist_ok=True)
    to_upload_root.mkdir(exist_ok=True)

    dropbox_path = f"dropbox:Cybershake/{cs_ver}"

 
    with open(files_to_sync,"r") as f:
        files_dict=yaml.safe_load(f)
 
    fault_names= sorted(files_dict.keys())
   
    uploaded={} 
    for fault_name in fault_names:
        #uploaded[fault_name]=[]
        update_uploaded(fault_name,[])
   
    tar_files = retrieve_dropbox_files(dropbox_path)
    print(tar_files)
    check_uploaded_tar_files(tar_files)


    print(f"#### Files already uploaded at {dropbox_path}")    
    print(uploaded)

    for fault_name in fault_names:

        # packing all data_types
        pack_ok={}.fromkeys(data_types)
        for data_type in data_types:
            if data_type not in uploaded[fault_name]:
                pack_ok[data_type]=pack(fault_name, data_type)
                if not pack_ok[data_type]:
                    print(f"{fault_name} {data_type} packing failed - Upload skipped")
                    continue
        # upload all data_types
        #TODO: upload only when needed
        upload_ok, tar_files_uploaded = upload(fault_name)
        if upload_ok:
            check_uploaded_tar_files(tar_files_uploaded) 


    print(f"#### Completed")
#
#    for fault_name in fault_names:
#        all_good = True
#        for data_type in data_types:
#            if not uploaded[fault_name][data_type]:
#                print(f"!!! {fault_name} {data_type} not uploaded")
#                all_good = False 
#        if all_good:
#            print(f"{fault_name} all synced successfully")
#            clean(fault_name)
#
#            
