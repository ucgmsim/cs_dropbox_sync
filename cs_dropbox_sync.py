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

data_types=['Source','IM','BB']


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


    args = parser.parse_args()
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

def pack(fault_name, data_type):

    work_dir=work_root/fault_name/data_type        
    tar_file=f"{fault_name}_{data_type}.tar"
    tar_path=work_root/fault_name/tar_file

    all_good = copy_files(fault_name, data_type, work_dir)
    if data_type == "Source":
        all_good = all_good and copy_files(fault_name, "VM", work_dir)

    # make tar file - not using tarfile package to avoid full-path when extracted
    if tar_path.exists():
        print(f"{tar_path} is deleted")
        tar_path.unlink() 
    
    tar_file=tar_path.name
    print(f"#### Making {tar_file}")
    p=subprocess.Popen(f"tar cvf ../{tar_file} *",cwd=str(work_dir),shell=True, stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()
    
    return all_good
    
def upload(fault_name, data_type):
    dropbox_dir = f"{dropbox_path}/{fault_name}"
    p=subprocess.Popen(f"rclone mkdir {dropbox_dir}",shell=True,stdout=subprocess.PIPE)
    p.communicate()

    tar_file=f"{fault_name}_{data_type}.tar"
    tar_path=work_root/fault_name/tar_file

    print(f"#### Uploading {tar_path.name} to {dropbox_dir}. Check progress with tail -f {tar_path}.log")
    with open(f"{tar_path}.log","w") as logfile:
        p=subprocess.Popen(f"rclone --progress copy {tar_path} {dropbox_dir}",shell=True,stdout=logfile, stderr=logfile)
        p.communicate()

    print(f"#### Uploading {tar_path.name} completed")

    p=subprocess.Popen(f"rclone ls {dropbox_dir}/{tar_path.name}",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    _,err= p.communicate()
    return (not err)

       
def update_uploaded(fault_name,data_type):
    if data_type == []:
        uploaded[fault_name]=[]
    else:
        uploaded[fault_name].append(data_type)
    with open(work_root/f"{fault_name}_{UPLOAD_REPORT}","w") as f:
        yaml.dump(uploaded[fault_name],f)

if __name__ == "__main__":
    args = load_args()

    global cs_root,work_root,dropbox_path,fpconf,files_to_sync, uploaded


    cs_root = args.cs_root
    files_to_sync = args.files_to_sync
    tmp_dir = args.tmp_dir

    nproc = args.nproc

    assert cs_root.exists()
    assert files_to_sync.exists()
    assert os.access(tmp_dir, os.X_OK | os.W_OK) # check if writing to tmp_dir is ok

    cs_ver = cs_root.name

    work_root = tmp_dir/f"{cs_ver}"

    dropbox_path = f"dropbox:/Cybershake/{cs_ver}"

 
    with open(files_to_sync,"r") as f:
        files_dict=yaml.safe_load(f)
 
    fault_names= sorted(files_dict.keys())
   
    uploaded={} 
    for fault_name in fault_names:
        #uploaded[fault_name]=[]
        update_uploaded(fault_name,[])

    p=subprocess.Popen(f"rclone ls {dropbox_path}",shell=True,stdout=subprocess.PIPE)
    out,err = p.communicate()
    lines = out.decode("utf-8").split("\n")


    for line in lines: # examine all files in dropbox_path
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
#           print(f"{fault_name} {data_type} {size}")
    #        uploaded[fault_name].append(data_type)
            update_uploaded(fault_name,data_type)

    print(f"#### Files already uploaded at {dropbox_path}")    
    print(uploaded)

    with open(FILE_PATTERN_CONF, "r") as f:
        fpconf = yaml.safe_load(f)


    for fault_name in fault_names:
        for data_type in data_types:
            if data_type not in uploaded[fault_name]:
                pack_ok=pack(fault_name, data_type)
                if pack_ok:
                    upload_ok=upload(fault_name, data_type)
                else:
                    print(f"{fault_name} {data_type} packing failed - Upload skipped")
                    continue
                if upload_ok:
                   # uploaded[fault_name].append(data_type)
                    update_uploaded(fault_name, data_type)

                else:
                    print(f"!!!!! FAIL   {fault_name} {data_type} upload failed")
#

    print(f"#### Successfully completed")
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
