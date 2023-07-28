// Defines endpoints and other constants

// Base URL
export const CS_API_URL = process.env.REACT_APP_CS_API_URL;

// Metadata Endpoints
export const GET_TECTONIC_TYPES_ENDPOINT = "/meta/tec_types";
export const GET_GRID_SPACING_ENDPOINT = "/meta/grid_spacing";
export const GET_RUN_TYPES_ENDPOINT = "/meta/run_types";
export const GET_DATA_TYPES_ENDPOINT = "/meta/data_types";

// Run Endpoints
export const GET_AVAILABLE_RUNS_ENDPOINT = "/runs/available";
export const GET_RUNS_INFO_ENDPOINT = "/runs/info";
