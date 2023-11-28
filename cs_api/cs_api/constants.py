from pathlib import Path

# Metadata endpoints
GET_TECTONIC_TYPES = "/meta/tec_types"
GET_GRID_SPACING = "/meta/grid_spacing"
GET_RUN_TYPES = "/meta/run_types"
GET_UNIQUE_FAULTS = "/meta/unique_faults"
GET_UNIQUE_SITES = "/meta/unique_sites"

# Run endpoints
GET_RUN_INFO = "/runs/info"
GET_RUNS_FROM_INTERESTS = "/runs/interests"
ADD_RUN = "/runs/add"

# Metadata Path
METADATA_FILE = Path(__file__).parent / "db" / "resources" / "run_metadata.yaml"
SITE_DF_FILE = Path(__file__).parent / "db" / "resources" / "site_df.csv"
DROPBOX_FILE = Path(__file__).parent / "db" / "resources" / "dropbox.csv"
