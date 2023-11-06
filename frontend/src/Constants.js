// Defines endpoints and other constants

// Base URL
export const CS_API_URL = process.env.REACT_APP_CS_API_URL;

// Metadata Endpoints
export const GET_TECTONIC_TYPES_ENDPOINT = "/meta/tec_types";
export const GET_GRID_SPACING_ENDPOINT = "/meta/grid_spacing";
export const GET_RUN_TYPES_ENDPOINT = "/meta/run_types";
export const GET_UNIQUE_FAULTS_ENDPOINT = "/meta/unique_faults";
export const GET_UNIQUE_SITES_ENDPOINT = "/meta/unique_sites";

// Run Endpoints
export const GET_RUNS_INFO_ENDPOINT = "/runs/info";
export const GET_RUNS_FROM_INTERESTS_ENDPOINT = "/runs/interests";
