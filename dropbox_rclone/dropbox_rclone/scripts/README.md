# Introduction
Upload/Download Cybershake run data to/from Dropbox.

# How to upload to Dropbox

## Assumptions
<img src="https://user-images.githubusercontent.com/466989/234416140-8722889b-b28c-42e5-8be2-0b59af1b3121.png" width="500" />

1. Cybershake archives are maintained under Cybershake dropbox folder, and Cybershake versions to be used in vYYpM format. (eg. v22p4 or v22p12)
2. Under Cybershake archive folder, let's say v20p5, we have list.txt (the list of faults and number of realisations per fault), and stocktake.csv, and folder for each fault.
3. Each fault folder, let's say HikWgtnmax, we have a TAR file for each data type, BB, Source and IM, named in `{fault_name}_{data_type}.tar` format, such as `HikWgtnmax_IM.tar`. If the archive file size is meant to be larger than 100Gb, we split them and name them with a suffix `_{num}.tar`, such as `HikWgtnmax_BB_0.tar`, `HikWgtnmax_BB_1.tar`, ... `HikWgtnmax_BB_6f.tar`. Note that the last one of the series has `f` character to indicate this is the last. From the `f`-suffixed tar file, we know HikWgtnmax BB was split into 7 files (0,1,..6). If this one or anything 0...5 is missing, we know this archive is incomplete or damaged.
4. The archive is meant to be kept tidy. Yet if any supplementary non-standard data should be stored, put them under a folder with name starting with `_` prefix. (eg. `_Faults_no_computed`) Upload/Download scripts will ignore anything in `_`-prefixed folder. 
<img src="https://user-images.githubusercontent.com/466989/234417066-0b6b84a2-94eb-45ed-bbe0-1f078faf5740.png" width="500" />

## Step 0. Make sure rclone is available.

On NeSI,
```
module add rclone
```
and make sure you have ~/.config/rclone/rclone.conf.


## Step 1. Edit sync_patterns.yaml

The script will select files to archive based on this YAML file. For each data type, it has `where` and `pattern` fields.

Note that Source pattern `{fault_name}.info` and `{fault_name}.csv` at lines 14-15 should be `Srf/{fault_name}.info` `Srf/{fault_name}.csv` for v22p12 and onwards.

```
  1 BB:
  2   where: "Runs/{fault_name}"
  3   pattern:
  4     - "*/BB/Acc/BB.bin"
  5 
  6 IM:
  7   where: "Runs/{fault_name}"
  8   pattern:
  9     - "*/IM_calc/{fault_name}*.csv"
 10 
 11 Source:
 12   where: "Data/Sources/{fault_name}"
 13   pattern:
 14     - "Srf/{fault_name}*.info"
 15     - "Srf/{fault_name}*.csv"
 16     - "Sim_params/{fault_name}*.yaml"
 17 
 18 VM:
 19   where: "Data/VMs/{fault_name}"
 20   pattern:
 21       - "vm_params.yaml"
 22       - "nzvm.cfg"
 23       - "${fault_name}_REL*.pertb.csv"

```

### Optional pattern
A pattern starting with `$` means it is *optional*. Currently only `*.pertb.csv` is optional.

When the script gets executed, it doesn't know if this CS run has perturbed VMs. 

During the run, if the script sees no file matching this pattern, it determines this run is not VM-perturbed. As `*.pertb.csv` pattern is marked as *optional*, the test passes if no match is found.

On the other hand, if it encounters any `*.pertb.csv`, it determins this run *is* VM-perturbed. Then we must find as many numbers of `*.pertb.csv` as RELs to pass the test.


## Step 2: Pre-process

Takes 2 inputs. The CS root directory, and the fault list file. *IMPORTANT:* it assumes your data is in CS standard structure. You could edit `sync_patterns.yaml` to accommodate a custom file structure.

Optional `--config` can be used to supply a modified version of `sync_patterns.yaml`. In this example, I edited line 14 and line 15 of `sync_patterns.yaml` to match the new pattern required by v22p12. 

```
 11 Source:
 12   where: "Data/Sources/{fault_name}"
 13   pattern:
 14     - "Srf/{fault_name}*.info"
 15     - "Srf/{fault_name}*.csv"
 16     - "Sim_params/{fault_name}*.yaml"

```

Then I supplied this `sync_patterns.yaml` as an optional argument `--config ./sync_patterns.yaml` as shown below.

eg. 
```
(python3_mahuika) baes@mahuika01: /nesi/nobackup/nesi00213/RunFolder/Cybershake/v22p12$ python $nobackup/baes/cs_dropbox_sync/cs_dropbox_preprocess.py ./ ./list.txt  --config sync_patterns.yaml 
['Source', 'IM', 'BB', 'VM', "SAMPLE_BB"]

...
OhariuC
- Check Source in Data/Sources/OhariuC
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
- Check IM in Runs/OhariuC
--  Check */IM_calc/*.csv
---   multiple expected: 31
---   Passed
- Check BB in Runs/OhariuC
--  Check */BB/Acc/BB.bin
---   multiple expected: 31
---   Passed
- Check VM in Data/VMs/OhariuC
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

======== Completed: Output files produced
      - /scale_wlg_nobackup/filesets/nobackup/nesi00213/RunFolder/Cybershake/v22p12/files_to_sync.yaml
      - /scale_wlg_nobackup/filesets/nobackup/nesi00213/RunFolder/Cybershake/v22p12/stocktake.csv

```
If all went well, you will have an output file `files_to_sync.yaml`, the list of files to uplad and `stocktake.csv` that shows the status of each data type and patterns.

The contents of `files_to_sync.yaml` may look like this.

```
  1 .:
  2   /scale_wlg_nobackup/filesets/nobackup/nesi00213/RunFolder/Cybershake/v22p12/stocktake.csv: 737
  3   list.txt: 50
  4 BooBooEAST:
  5   BB:
  6     Runs/BooBooEAST/BooBooEAST_REL01/BB/Acc/BB.bin: 1560129496
  7     Runs/BooBooEAST/BooBooEAST_REL02/BB/Acc/BB.bin: 1560129496
  8     Runs/BooBooEAST/BooBooEAST_REL03/BB/Acc/BB.bin: 1560129496
  9     Runs/BooBooEAST/BooBooEAST_REL04/BB/Acc/BB.bin: 1560129496
...
 39   IM:
 40     Runs/BooBooEAST/BooBooEAST_REL01/IM_calc/BooBooEAST_REL01.csv: 21973502
 41     Runs/BooBooEAST/BooBooEAST_REL02/IM_calc/BooBooEAST_REL02.csv: 22033778
 42     Runs/BooBooEAST/BooBooEAST_REL03/IM_calc/BooBooEAST_REL03.csv: 22042162
 43     Runs/BooBooEAST/BooBooEAST_REL04/IM_calc/BooBooEAST_REL04.csv: 22016286
 ...
 73   Source:
 74     Data/Sources/BooBooEAST/Srf/BooBooEAST.csv: 1506
 75     Data/Sources/BooBooEAST/Srf/BooBooEAST.info: 7088
 76     Data/Sources/BooBooEAST/Srf/BooBooEAST_REL01.csv: 1552
 77     Data/Sources/BooBooEAST/Srf/BooBooEAST_REL01.info: 7088
 ...
142   VM:
143     Data/VMs/BooBooEAST/BooBooEAST_REL01.pertb.csv: 196
144     Data/VMs/BooBooEAST/BooBooEAST_REL02.pertb.csv: 196
145     Data/VMs/BooBooEAST/BooBooEAST_REL03.pertb.csv: 197
146     Data/VMs/BooBooEAST/BooBooEAST_REL04.pertb.csv: 195
...
176     Data/VMs/BooBooEAST/nzvm.cfg: 439
177     Data/VMs/BooBooEAST/vm_params.yaml: 994
..
210   SAMPLE_BB:
211     Runs/BooBooEAST/BooBooEAST_REL01/BB/Acc/BB.bin: 1560129496


```

For each fault in a separate section of YAML, we have subsections for each data type, BB, IM, Source, VM and list of files and their size, where the size will be used to verify if the copy of file is good.
At the top level, there is "." section that includes `list.txt` and `stocktake.csv`, which contain the essential information about the integrity of this data archive. We will keep them in Dropbox too.

By default, this script will check every data type. However, if you wish to process specific data type only (eg. if you only have BB data to upload), you can use `-t` option. eg. `-t BB`. We have only 4 choices. `BB`,`IM`,`Source` and `SAMPLE_BB`  - notice that there is no `VM`, even if `files_to_sync.yaml` does have a subsection for VM. Just use `Source` instead - Both Source and VM data are archived into a same TAR file anyway.

`SAMPLE_BB` is usually the BB.bin of the median event if available, or of the first realisation.
## Step 3. Upload

If all good, we can start upload files using `cs_dropbox_upload.py`. It uses two mandatory arguments.
```
usage: cs_dropbox_upload.py [-h] [--tmp_dir TMP_DIR] [-t {Source,IM,BB}] [-f] [--no_checksum]
                            cs_root files_to_sync

positional arguments:
  cs_root               Path to CS root
  files_to_sync         YAML file keeping the list of files to sync

optional arguments:
  -h, --help            show this help message and exit
  --tmp_dir TMP_DIR     Temp directory where files to be copied to and
                        uploaded from
  -t {Source,IM,BB}, --data_types {Source,IM,BB}
                        Data types to download. Gets all BB, IM, Source if not
                        specified
  -f, --overwrite       Force uploading even if it has been previously
                        uploaded
  --no_checksum         Skip rclone check after uploading
```

Note that `files_to_sync` is the output file from Step 2. 

Let's have another peek.

```
  1 .:
  2   /scale_wlg_nobackup/filesets/nobackup/nesi00213/RunFolder/Cybershake/v22p12/stocktake.csv: 737
  3   list.txt: 50
  4 BooBooEAST:
  5   BB:
  6     Runs/BooBooEAST/BooBooEAST_REL01/BB/Acc/BB.bin: 1560129496
  7     Runs/BooBooEAST/BooBooEAST_REL02/BB/Acc/BB.bin: 1560129496
  8     Runs/BooBooEAST/BooBooEAST_REL03/BB/Acc/BB.bin: 1560129496
...
```
As previously explained, this file contains a structured list of files to be uploaded, and their file size (used for verification before making a TAR ball).

The upload script will copy these files from the original location to a temp directory, make 3 TAR balls (Source, IM and BB) (by default, unless you specify otherwise with `-t` option) and upload them to Dropbox. 

Note that uploading can take a VERY LONG time, so it's best to run this in a `screen` session.

Let's give a demo run.
```
(python3_mahuika) baes@mahuika01: /nesi/nobackup/nesi00213/RunFolder/Cybershake/v22p12$ python $nobackup/baes/cs_dropbox_sync/cs_dropbox_upload.py ./ ./files_to_sync.yaml 
#### Uploading misc files from root
#### Files in dropbox:Cybershake/v22p12
 --list.txt
 --stocktake.csv
 --Moonshine_BB.tar
 --Moonshine_IM.tar
 --BooBooEAST_BB.tar
 --BooBooEAST_IM.tar
 --OhariuC_BB.tar
 --OhariuC_IM.tar
 --DryHuang_BB.tar
 --DryHuang_IM.tar
#### Files already uploaded at dropbox:Cybershake/v22p12
{'BooBooEAST': ['BB', 'IM'], 'DryHuang': ['BB', 'IM'], 'Moonshine': ['BB', 'IM'], 'OhariuC': ['BB', 'IM']}

```

Pause here and have a look at the output.
The upload script starts with uploading `list.txt` and `stocktake.csv` to Dropbox. The Dropbox link is automatically inferred, in this case `dropbox:Cybershake/v22p12`. Then, it scans the files currently in this Dropbox folder, and examines if we already have uploaded something. It will skip uploading TAR files that already exist. This is useful, especially when you upload portions of data progressivly at a time. 
Use `--overwrite` argument if you want to enforce uploading.

In this example, we can see that all 4 faults already have BB and IM tar files uploaded, meaning we will be only archiving Source data.


Let's carry on. You will see how each fault data is processed. 

```
-------------------------------
        BooBooEAST

-------------------------------

#### Info: tmp/v22p12/to_upload/BooBooEAST already exists. Delete
#### Copy BooBooEAST Source files to tmp/v22p12/to_pack/BooBooEAST/Source
#### Copy BooBooEAST VM files to tmp/v22p12/to_pack/BooBooEAST/Source
#### Making tmp/v22p12/to_upload/BooBooEAST/BooBooEAST_Source.tar
tar cvf /scale_wlg_nobackup/filesets/nobackup/nesi00213/RunFolder/Cybershake/v22p12/tmp/v22p12/to_upload/BooBooEAST/BooBooEAST_Source.tar BooBooEAST.csv BooBooEAST.info BooBooEAST_REL01.csv BooBooEAST_REL01.info BooBooEAST_REL01.pertb.csv BooBooEAST_REL02.csv BooBooEAST_REL02.info BooBooEAST_REL02.pertb.csv BooBooEAST_REL03.csv BooBooEAST_REL03.info BooBooEAST_REL03.pertb.csv BooBooEAST_REL04.csv BooBooEAST_REL04.info BooBooEAST_REL04.pertb.csv BooBooEAST_REL05.csv BooBooEAST_REL05.info BooBooEAST_REL05.pertb.csv BooBooEAST_REL06.csv BooBooEAST_REL06.info BooBooEAST_REL06.pertb.csv BooBooEAST_REL07.csv BooBooEAST_REL07.info BooBooEAST_REL07.pertb.csv BooBooEAST_REL08.csv BooBooEAST_REL08.info BooBooEAST_REL08.pertb.csv BooBooEAST_REL09.csv BooBooEAST_REL09.info BooBooEAST_REL09.pertb.csv BooBooEAST_REL10.csv BooBooEAST_REL10.info BooBooEAST_REL10.pertb.csv BooBooEAST_REL11.csv BooBooEAST_REL11.info BooBooEAST_REL11.pertb.csv BooBooEAST_REL12.csv BooBooEAST_REL12.info BooBooEAST_REL12.pertb.csv BooBooEAST_REL13.csv BooBooEAST_REL13.info BooBooEAST_REL13.pertb.csv BooBooEAST_REL14.csv BooBooEAST_REL14.info BooBooEAST_REL14.pertb.csv BooBooEAST_REL15.csv BooBooEAST_REL15.info BooBooEAST_REL15.pertb.csv BooBooEAST_REL16.csv BooBooEAST_REL16.info BooBooEAST_REL16.pertb.csv BooBooEAST_REL17.csv BooBooEAST_REL17.info BooBooEAST_REL17.pertb.csv BooBooEAST_REL18.csv BooBooEAST_REL18.info BooBooEAST_REL18.pertb.csv BooBooEAST_REL19.csv BooBooEAST_REL19.info BooBooEAST_REL19.pertb.csv BooBooEAST_REL20.csv BooBooEAST_REL20.info BooBooEAST_REL20.pertb.csv BooBooEAST_REL21.csv BooBooEAST_REL21.info BooBooEAST_REL21.pertb.csv BooBooEAST_REL22.csv BooBooEAST_REL22.info BooBooEAST_REL22.pertb.csv BooBooEAST_REL23.csv BooBooEAST_REL23.info BooBooEAST_REL23.pertb.csv BooBooEAST_REL24.csv BooBooEAST_REL24.info BooBooEAST_REL24.pertb.csv BooBooEAST_REL25.csv BooBooEAST_REL25.info BooBooEAST_REL25.pertb.csv BooBooEAST_REL26.csv BooBooEAST_REL26.info BooBooEAST_REL26.pertb.csv BooBooEAST_REL27.csv BooBooEAST_REL27.info BooBooEAST_REL27.pertb.csv BooBooEAST_REL28.csv BooBooEAST_REL28.info BooBooEAST_REL28.pertb.csv BooBooEAST_REL29.csv BooBooEAST_REL29.info BooBooEAST_REL29.pertb.csv BooBooEAST_REL30.csv BooBooEAST_REL30.info BooBooEAST_REL30.pertb.csv BooBooEAST_REL31.csv BooBooEAST_REL31.info BooBooEAST_REL31.pertb.csv BooBooEAST_REL32.csv BooBooEAST_REL32.info BooBooEAST_REL32.pertb.csv BooBooEAST_REL33.csv BooBooEAST_REL33.info BooBooEAST_REL33.pertb.csv nzvm.cfg vm_params.yaml

#### Uploading tmp/v22p12/to_upload/BooBooEAST to dropbox:Cybershake/v22p12/BooBooEAST.


 --------   Check progress with     tail -f /scale_wlg_nobackup/filesets/nobackup/nesi00213/RunFolder/Cybershake/v22p12/tmp/v22p12/to_upload/BooBooEAST_progress.log


#### Uploading tmp/v22p12/to_upload/BooBooEAST completed
#### Files in dropbox:Cybershake/v22p12/BooBooEAST
 --BooBooEAST_BB.tar
 --BooBooEAST_IM.tar
 --BooBooEAST_Source.tar
...
```

It performs these steps.
1. Copies files to sync to a temporary directory eg.`tmp/v22p12/to_pack/BooBooEAST/Source`
2. Make TAR file(s). If a TAR file is meant to exceed 100Gb, it will tar them into multiple pieces, naming them {faultname}_{datatype}_{num}.tar. eg. `BooBooEAST_BB_1.tar`, `BooBooEAST_BB_2.tar`,...`BooBooEAST_BB_4f.tar`. Notice that the last one has an extra "f" marker in the {num} bit. This is to let the script know how many pieces need to be present to consider BooBooEAST_BB is complete.
3. A temporary `to_upload` directory (eg. `tmp/v22p12/to_upload/BooBooEAST` ) has TAR files to upload. The external program `rclone` is executed to copy everything in this directory to the Dropbox folder. Automatically rclone will upload multiple files in parallel, which is much faster than uploading one file at a time.
4. After upload, `rclone` checks the presence of uploaded TAR files. See below for File integirty and verification.
5. During the upload, the progress output from `rclone` is written to a separate file. You can check the progress by `tail -f ....` command as instructed on the screen.

Open another terminal, and try `tail -f ...` command. Usually this is helpful to see the progress of large BB.tar files.

```
Transferring:
 *                             BooBooEAST_BB.tar:  2% /47.948Gi, 7.857Mi/s, 1h41Transferred:   	    1.078 GiB / 47.948 GiB, 2%, 7.857 MiB/s, ETA 1h41m48s
Transferred:            0 / 1, 0%
Elapsed time:       2m5.0s

```


## File integrity and verification
We assume files to be archived are good, and don't check the integrity of individual file, which is beyond the scope of this code. 
However, we consider the following steps to ensure files are correctly packaged and archived on Dropbox.
1. Check if everything is in place. Done by `cs_dropbox_preprocess.py`. Based on sync_patterns.yaml, it finds all the files that match the pattern, and generates `stocktake.csv` to review what is included and what is missing.
2. Check if the copied version is identical to the original before making a TAR file : Done by `cs_dropbox_upload.py`. The files_to_sync.yaml contains the file size info. If both files have the same file size, we consider they are identical. (Checksum is an overkill for local file copy)
3. After a TAR file is created, files contained are compared against the original, and *aborts* if there are issues (eg. file storage going low, producing incomplete TAR file).
4. Dropbox upload: rclone copy automatically checks the size and mod time, which is believed to be sufficient to (full scale checksum is slow). Also rclone discards the copy if the file is half-finished or tampered. If "rclone ls" returns the file from Dropbox, it is *almost* guaranteed to be the exact copy (See https://forum.rclone.org/t/rclone-copy-files-and-checksum/14895/2). Having said that, a "rclone check" step is explicitly executed for extra safety (See https://rclone.org/commands/rclone_check/ ). The overhead for this extra check is little.
5. After all the upload is complete, the upload script will traverse the remote storage and double-checks all the *supposedly uploaded* files are indeed there, and returns the final summary.



# How to download from Dropbox

To retrive a cybershake archive data from Dropbox, use `cs_dropbox_download.py`. This allows you to select the cybershake version, specific data types, and faults to download, and untar them in the specified path. 

A number of options have been implemented to accommodate a variety of use cases. 
```
usage: cs_dropbox_download.py [-h] [-t {Source,IM,BB}] [--download_dir DOWNLOAD_DIR] [--cleanup] [--no_download] [--inc_fault INC_FAULT] [--exc_fault EXC_FAULT] [--force_untar] dropbox_cs_ver

positional arguments:
  dropbox_cs_ver        CS ver stored in Dropbox

optional arguments:
  -h, --help            show this help message and exit
  -t {Source,IM,BB}, --data_types {Source,IM,BB}
                        Data types to download. Gets all BB, IM, Source if not specified
  --download_dir DOWNLOAD_DIR
                        Download directory. Current directory if not specified
  --cleanup             Delete *.tar files after extraction
  --no_download         If download has been already done, and wish to untar only
  --inc_fault INC_FAULT
                        Include this fault. All if unspecified.
  --exc_fault EXC_FAULT
                        Exclude this fault. The fault is excluded if both inc_fault exc_fault are specified
  --force_untar         Force untar from scratch

```
