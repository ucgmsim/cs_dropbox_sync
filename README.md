# cs_dropbox_upload
Upload Cybershake runs to Dropbox

# How to run

## Step 0. Make sure rclone is available.

On NeSI,
```
module add rclone
```
and make sure you have ~/.config/rclone/rclone.conf.


## Step 1. Edit sync_patterns.yaml

The script will select files to archive based on this YAML file. For each data type, it has `where` and `pattern` fields.

Note that Source pattern `Srf/{fault_name}.info` and `Srf/{fault_name}.csv`used to be `{fault_name}.info` `{fault_name}.csv` pre v22p12.

```
  1 BB:
  2   where: "Runs/{fault_name}"
  3   pattern:
  4     - "*/BB/Acc/BB.bin"
  5 
  6 IM:
  7   where: "Runs/{fault_name}"
  8   pattern:
  9     - "*/IM_calc/*.csv"
 10 
 11 Source:
 12   where: "Data/Sources/{fault_name}"
 13   pattern:
 14     - "Srf/{fault_name}.info"
 15     - "Srf/{fault_name}.csv"
 16     - "Srf/*REL*.info"
 17     - "Srf/*REL*.csv"
 18 
 19 VM:
 20   where: "Data/VMs/{fault_name}"
 21   pattern:
 22       - "vm_params.yaml"
 23       - "nzvm.cfg"
 24       - "$*.pertb.csv"
~                                

```

### Optional pattern
A pattern starting with `$` means it is *optional*. Currently only `*.pertb.csv` is optional.

When the script gets executed, it doesn't know if this CS run has perturbed VMs. 

During the run, if the script sees no file matching this pattern, it determines this run is not VM-perturbed. So the test passes if no `*.pertb.csv` is found.

On the other hand, if it encounters any `*.pertb.csv`, it determins this run *is* VM-perturbed, and the test only passes if as many numbers of `*.pertb.csv` as RELs are found/



## Step 2: Check the integrity of the CS run

Takes 2 inputs. The CS root directory, and the fault list file.

eg. 
```
(python3_mahuika) baes@mahuika01: ~/cs_dropbox_upload$ python cs_run_verify.py /nesi/nobackup/nesi00213/RunFolder/Cybershake/v22p12 /nesi/nobackup/nesi00213/RunFolder/Cybershake/v22p12/list.txt 

...

OhariuC
- Check BB in /nesi/nobackup/nesi00213/RunFolder/Cybershake/v22p12/Runs/OhariuC
--  Check */BB/Acc/BB.bin
---   multiple expected: 31
---   Passed
- Check IM in /nesi/nobackup/nesi00213/RunFolder/Cybershake/v22p12/Runs/OhariuC
--  Check */IM_calc/*.csv
---   multiple expected: 31
---   Passed
- Check Source in /nesi/nobackup/nesi00213/RunFolder/Cybershake/v22p12/Data/Sources/OhariuC
--  Check Srf/OhariuC.info
---   single expected: True
---   Passed
--  Check Srf/OhariuC.csv
---   single expected: True
---   Passed
--  Check Srf/*REL*.info
---   multiple expected: 31
---   Passed
--  Check Srf/*REL*.csv
---   multiple expected: 31
---   Passed
- Check VM in /nesi/nobackup/nesi00213/RunFolder/Cybershake/v22p12/Data/VMs/OhariuC
--  Check vm_params.yaml
---   single expected: True
---   Passed
--  Check nzvm.cfg
---   single expected: True
---   Passed
--  Check $*.pertb.csv
---   $*.pertb.csv is optional
---   multiple expected: 31
---   Now, must find 31
---   Passed

======== Completed. List of files to sync is written to /scale_wlg_persistent/filesets/home/baes/cs_dropbox_upload/files_to_sync.yaml

```
If all went well, you will have an output file `files_to_sync.yaml`, the list of files to upload. 

If there is anything missing, AssertionError will catch it.

```
- Check Source in /nesi/nobackup/nesi00213/RunFolder/Cybershake/v22p12/Data/Sources/BooBooEAST
--  Check BooBooEAST.info
---   single expected: False
Traceback (most recent call last):
  File "cs_run_verify.py", line 98, in <module>
    test_all_exist(data_type, fault_name)
  File "cs_run_verify.py", line 59, in test_all_exist
    assert found, "---   FAILED !!!!!!!"
AssertionError: ---   FAILED !!!!!!!

```
In this case, `BooBooEAST.info` was not found in `/nesi/nobackup/nesi00213/RunFolder/Cybershake/v22p12/Data/Sources/BooBooEAST`.

## Step 3. Upload

If all good, we can start upload files using `cs_dropbox_upload.py`. It uses 3 arguments. 
```
usage: cs_dropbox_upload.py [-h] [--nproc NPROC] cs_root files_to_sync tmp_dir

positional arguments:
  cs_root        Path to CS root
  files_to_sync  YAML file keeping the list of files to sync
  tmp_dir        Temp directory where files to be copied to and uploaded from

optional arguments:
  -h, --help     show this help message and exit
```

Note that `files_to_sync` is the output file from Step 2. 

Let's have a peek.

```

(python3_mahuika) baes@mahuika01: ~/cs_dropbox_upload$ head -10 files_to_sync.yaml 
BooBooEAST:
  BB:
    /nesi/nobackup/nesi00213/RunFolder/Cybershake/v22p12/Runs/BooBooEAST/BooBooEAST_REL01/BB/Acc/BB.bin: 1560129496
    /nesi/nobackup/nesi00213/RunFolder/Cybershake/v22p12/Runs/BooBooEAST/BooBooEAST_REL02/BB/Acc/BB.bin: 1560129496
    /nesi/nobackup/nesi00213/RunFolder/Cybershake/v22p12/Runs/BooBooEAST/BooBooEAST_REL03/BB/Acc/BB.bin: 1560129496
    /nesi/nobackup/nesi00213/RunFolder/Cybershake/v22p12/Runs/BooBooEAST/BooBooEAST_REL04/BB/Acc/BB.bin: 1560129496
    /nesi/nobackup/nesi00213/RunFolder/Cybershake/v22p12/Runs/BooBooEAST/BooBooEAST_REL05/BB/Acc/BB.bin: 1560129496
    /nesi/nobackup/nesi00213/RunFolder/Cybershake/v22p12/Runs/BooBooEAST/BooBooEAST_REL06/BB/Acc/BB.bin: 1560129496
    /nesi/nobackup/nesi00213/RunFolder/Cybershake/v22p12/Runs/BooBooEAST/BooBooEAST_REL07/BB/Acc/BB.bin: 1560129496
    /nesi/nobackup/nesi00213/RunFolder/Cybershake/v22p12/Runs/BooBooEAST/BooBooEAST_REL08/BB/Acc/BB.bin: 1560129496
...
```
This file contains a structured list of files to be uploaded, and their file size (used for verification before making a TAR ball).

This script will copy these files from the original location to a temp directory, make 3 TAR balls (Source, IM and BB) and upload to Dropbox.

Note that uploading can take a VERY LONG time, so it's best to run this in a `screen` session.

```
(python3_mahuika) baes@mahuika01: ~/cs_dropbox_upload$ python cs_dropbox_upload.py /nesi/nobackup/nesi00213/RunFolder/Cybershake/v22p12 ./files_to_sync.yaml /nesi/nobackup/nesi00213/tmp/baes
#### Files already uploaded at dropbox:/Cybershake/v22p12
{'BooBooEAST': [], 'DryHuang': [], 'Moonshine': [], 'OhariuC': []}
#### Copy BooBooEAST Source files to /nesi/nobackup/nesi00213/tmp/baes/v22p12/BooBooEAST/Source
#### Copy BooBooEAST VM files to /nesi/nobackup/nesi00213/tmp/baes/v22p12/BooBooEAST/Source
/nesi/nobackup/nesi00213/tmp/baes/v22p12/BooBooEAST/BooBooEAST_Source.tar is deleted
#### Making BooBooEAST_Source.tar
#### Uploading BooBooEAST_Source.tar to dropbox:/Cybershake/v22p12/BooBooEAST. Check progress with tail -f /nesi/nobackup/nesi00213/tmp/baes/v22p12/BooBooEAST/BooBooEAST_Source.tar.log
#### Uploading BooBooEAST_Source.tar completed
#### Copy BooBooEAST IM files to /nesi/nobackup/nesi00213/tmp/baes/v22p12/BooBooEAST/IM
/nesi/nobackup/nesi00213/tmp/baes/v22p12/BooBooEAST/BooBooEAST_IM.tar is deleted
#### Making BooBooEAST_IM.tar
#### Uploading BooBooEAST_IM.tar to dropbox:/Cybershake/v22p12/BooBooEAST. Check progress with tail -f /nesi/nobackup/nesi00213/tmp/baes/v22p12/BooBooEAST/BooBooEAST_IM.tar.log
#### Uploading BooBooEAST_IM.tar completed
#### Copy BooBooEAST BB files to /nesi/nobackup/nesi00213/tmp/baes/v22p12/BooBooEAST/BB
#### Making BooBooEAST_BB.tar
#### Uploading BooBooEAST_BB.tar to dropbox:/Cybershake/v22p12/BooBooEAST. Check progress with tail -f /nesi/nobackup/nesi00213/tmp/baes/v22p12/BooBooEAST/BooBooEAST_BB.tar.log

...

```
During the upload, the progress output from `rclone` is written to a separate file. You can check the progress by `tail -f ....` command as instructed on the screen.
Open another terminal, and try

```
Transferring:
 *                             BooBooEAST_BB.tar:  2% /47.948Gi, 7.857Mi/s, 1h41Transferred:   	    1.078 GiB / 47.948 GiB, 2%, 7.857 MiB/s, ETA 1h41m48s
Transferred:            0 / 1, 0%
Elapsed time:       2m5.0s

```

For each fault, there will be 3 uploads, Source (which includes both Source and VM data), IM, and BB tar files. 
Upon each upload, it will update a progress file under `tmp_dir`. The progress file name is {fault_name}_progress.yaml.

```
(python3_mahuika) baes@mahuika01: /nesi/nobackup/nesi00213/tmp/baes/v22p12$ cat BooBooEAST_progress.yaml
- Source
- IM

```
, meaning Source and IM uplad have been completed.

# File integrity and verification
The integrity of individual file is *NOT* tested by this code. However, we considered the following steps to make sure the files don't get corrupted.
1. Check if everything is in place. Done by `cs_run_verify.py`. 
2. Check if the copied version is identical to the original before making a TAR ball : Done by `cs_dropbox_upload.py`. The files_to_sync.yaml contains the file size info. If both files have the same file size, we consider they are identical. (Checksum is an overkill for local file copy)
3. We assume making a TAR file is error-free.
4. Dropbox upload: rclone upload is known to do the checksum test, and the file upload is *atomic*, meaning it is all or nothing. If it is found on Dropbox, it is guaranteed to be identical to the original. 

