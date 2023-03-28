import argparse
import hashlib
import pandas as pd
from pathlib import Path
import yaml

CONFIG="sync_patterns.yaml"
OPTIONAL_PATTERN_MARKER="$"

STOCKTAKE_CSV="stocktake.csv"

#cs_root=Path("/scratch/x2568a02/UC/RunFolder/Cybershake/v22p4")
FILES_DICT_FILE = Path().cwd()/"files_to_sync.yaml"
DATA_TYPES = ['Source','IM','BB']


def load_args():
    parser= argparse.ArgumentParser()
    parser.add_argument(
        "cs_root",type=Path, help="Path to CS root", default=Path.cwd()
    )
    parser.add_argument(
        "fault_list",type=Path, help="List of fault and its realisation numbers", default=Path.cwd()/"list.txt")
    parser.add_argument(
        "--config", type=Path, help="Config file containing file patterns to sync", default=Path(__file__).parent.resolve()/CONFIG)
    parser.add_argument(
        "--out_file",type=Path, help="List of files to sync", default=FILES_DICT_FILE
    )
    parser.add_argument(
        "--stocktake_csv", type=Path, help="Stocktake CSV file", default=Path.cwd()/STOCKTAKE_CSV)
    parser.add_argument(
        '-t', "--data_types", help="Data types to download. Gets all BB, IM, Source if not specified",action='append', choices=DATA_TYPES, default=[])

    args = parser.parse_args()

    if args.data_types == []:
        args.data_types = DATA_TYPES

    return args


def cherrypick_files(where, pattern, num):

    optional=False
    if pattern.startswith(OPTIONAL_PATTERN_MARKER):
        print(f"---   {pattern} is optional")
        pattern=pattern.strip(OPTIONAL_PATTERN_MARKER)
        optional=True

    if "*" in pattern: #looking for multiple
        result=list(where.glob(pattern))
        print(result)
        print(f"---   multiple expected: {num}")
        if optional:
            if len(result) > 0: #ok, now this MUST match num (ie. no longer optional)
                print(f"---   Now, must find {num}")
                optional=False
        found = (not optional and len(result)==num)
        return found, result
    else: #single match
        found = Path(where/pattern).exists()
        print(f"---   single expected: {found}")
        files = [Path(where/pattern)] if found else []

# TODO: thw following might be needed for completeness, but we have no use for this yet.
#        if optional:
#            return True, [Path(where/pattern)] if found else []
        return found, files

        
def test_all_exist(data_type, fault_name):

    files_dict[fault_name][data_type]={}
    where = cs_root / config[data_type]['where'].format(fault_name=fault_name)#
    print(f"- Check {data_type} in {where}")
    for pat in config[data_type]['pattern']:
        wpat=pat.format(fault_name="*")
        col_num = f"num({data_type}_{wpat})"
        col_ok = f"OK({data_type}_{wpat})"
        pat = pat.format(fault_name=fault_name)
        print(f"--  Check {pat}")
        found, files = cherrypick_files(where, pat, rel_num_dict[fault_name])
        if found:
            print("---   Passed")
            for f in files:
                files_dict[fault_name][data_type][str(f)]=f.stat().st_size

        else:
            print(f"---   FAILED: {fault_name} {data_type} found {len(files)} !!!!!!!")
           #        print(files)

        stocktake_df[col_num].loc[fault_name]=len(files)
        stocktake_df[col_ok].loc[fault_name]=found


if __name__ == "__main__":

    global config, rel_num_dict, files_dict, stocktake_df


    args = load_args()

    cs_root = args.cs_root
    fault_list = args.fault_list
    out_file = args.out_file
    data_types = args.data_types
    config = args.config
    stocktake_csv = args.stocktake_csv

    assert cs_root.exists()
    assert fault_list.exists()


    if "Source" in data_types:
        data_types.append("VM") #if Source is in, add VM too

    print(data_types)

    

    rel_num_dict={}
    with open(fault_list,"r") as f:
        lines=f.readlines()
        for line in lines:
            fault_name, num_rels = line.split()
            rel_num_dict[fault_name]=int(num_rels.split("r")[0])

    assert config.exists()

    with open(config,'r') as f:
        config=yaml.safe_load(f)
    
    stocktake_df = pd.DataFrame(list(rel_num_dict.values()), index=list(rel_num_dict.keys()), columns=['rel_nums'])

    for data_type in DATA_TYPES: #stoktake CSV file is made for ALL data_types and patterns
        for pat in config[data_type]['pattern']:
            wpat=pat.format(fault_name="*")
            col_num = f"num({data_type}_{wpat})"
            col_ok = f"OK({data_type}_{wpat})"

            stocktake_df[col_num]=0
            stocktake_df[col_ok]=False


    files_dict={} 
    for fault_name in list(rel_num_dict.keys()):
        print(f"{fault_name}")
        files_dict[fault_name]={}
        for data_type in data_types:
            files_dict[fault_name][data_type]={}
            test_all_exist(data_type, fault_name)

    stocktake_df.to_csv(stocktake_csv)
    
    files_dict["."]={} # special section to list stocktake.csv and list.txt
    files_dict["."][str(fault_list)]= fault_list.stat().st_size
    files_dict["."][str(stocktake_csv)] = stocktake_csv.stat().st_size

    print(files_dict)
    with open(out_file,"w") as f:
        yaml.dump(files_dict,f)

    print(f"======== Completed: Output files produced"
    print(f"      - {out_file}")
    print(f"      - {stocktake_csv}")

