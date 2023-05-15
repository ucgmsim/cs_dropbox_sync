from pathlib import Path

# Metadata endpoints
GET_TECTONIC_TYPES = "/meta/tec_types"
GET_GRID_SPACING = "/meta/grid_spacing"
GET_SCIENTIFIC_VERSION = "/meta/scientific_version"

# Run endpoints
GET_AVAILABLE_RUNS = "/runs/available"
GET_RUN_INFO = "/runs/info"

# Metadata Path
METADATA_FILE = Path(__file__).parent / "run_metadata.yaml"
