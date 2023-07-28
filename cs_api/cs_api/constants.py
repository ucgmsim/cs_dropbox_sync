from pathlib import Path

# Metadata endpoints
GET_TECTONIC_TYPES = "/meta/tec_types"
GET_GRID_SPACING = "/meta/grid_spacing"
GET_RUN_TYPES = "/meta/run_types"
GET_DATA_TYPES = "/meta/data_types"

# Run endpoints
GET_AVAILABLE_RUNS = "/runs/available"
GET_RUN_INFO = "/runs/info"

# Metadata Path
METADATA_FILE = Path(__file__).parent / "db" / "run_metadata.yaml"
