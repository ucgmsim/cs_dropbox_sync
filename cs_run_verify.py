import argparse
import hashlib

from pathlib import Path
import yaml

CONFIG="sync_patterns.yaml"
OPTIONAL_PATTERN_MARKER="$"

#cs_root=Path("/scratch/x2568a02/UC/RunFolder/Cybershake/v22p4")
FILES_DICT_FILE = Path().cwd()/"files_to_sync.yaml"


def load_args():
    parser= argparse.ArgumentParser()
    parser.add_argument(
        "cs_root",type=Path, help="Path to CS root", default=Path.cwd()
    )
    parser.add_argument(
        "fault_list",type=Path, help="List of fault and its realisation numbers", default=Path.cwd()/"list.txt")
    parser.add_argument(
        "--out_file",type=Path, help="List of files to sync", default=FILES_DICT_FILE
    )
    args = parser.parse_args()
    return args


def cherrypick_files(where, pattern, num):

    optional=False
    if pattern.startswith(OPTIONAL_PATTERN_MARKER):
        print(f"---   {pattern} is optional")
        pattern=pattern.strip(OPTIONAL_PATTERN_MARKER)
        optional=True

    if "*" in pattern: #looking for multiple
        result=list(where.glob(pattern))
        print(f"---   multiple expected: {len(result)}")
        if optional:
            if len(result) > 0: #ok, now this MUST match num (ie. no longer optional)
                print(f"---   this is a MUST")
                optional=False
        return (not optional and len(result)==num), result
    else: #single match
        found = Path(where/pattern).exists()
        print(f"---   single expected: {found}")
        return found, [Path(where/pattern)]

        
def test_all_exist(data_type, fault_name):

    files_dict[fault_name][data_type]={}
    where = cs_root / config[data_type]['where'].format(fault_name=fault_name)#
    print(f"- Check {data_type} in {where}")
    for pat in config[data_type]['pattern']:
        pat = pat.format(fault_name=fault_name)
        print(f"--  Check {pat}")
        found, files = cherrypick_files(where, pat, rel_num_dict[fault_name])
        assert found, "---   FAILED !!!!!!!"
        print("---   Passed")

        for f in files:
           files_dict[fault_name][data_type][str(f)]=f.stat().st_size
#        print(files)



if __name__ == "__main__":
    args = load_args()

    cs_root = args.cs_root
    fault_list = args.fault_list
    out_file = args.out_file

    assert cs_root.exists()
    assert fault_list.exists()

    global config, rel_num_dict, files_dict



    rel_num_dict={}
    with open(fault_list,"r") as f:
        lines=f.readlines()
        for line in lines:
            fault_name, num_rels = line.split()
            rel_num_dict[fault_name]=int(num_rels.split("r")[0])

    with open(CONFIG,'r') as f:
        config=yaml.safe_load(f)
    
    files_dict={} 
    for fault_name in list(rel_num_dict.keys()):
        print(f"{fault_name}")
        files_dict[fault_name]={}
        for data_type in config.keys():
            files_dict[fault_name][data_type]={}
            test_all_exist(data_type, fault_name)

    with open(out_file,"w") as f:
        yaml.dump(files_dict,f)

    print(f"======== Completed. List of files to sync is written to {out_file}")
