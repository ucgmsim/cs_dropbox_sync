import React, {useEffect, useState, memo,} from "react";
import Select from "react-select";
import AsyncSelect from 'react-select/async';

import * as CONSTANTS from "Constants";

import "assets/AddRun.css";
import {Button} from "react-bootstrap";
import {TextField} from "@mui/material";
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import {APIQueryBuilder} from "./Utils";
import {ADD_RUN_ENDPOINT} from "Constants";

const AddRun = ({setReturn}) => {
  const [runName, setRunName] = useState("");
  const [dropboxFolder, setDropboxFolder] = useState("");
  const [runType, setRunType] = useState("");
  const [gridSpacing, setGridSpacing] = useState("");
  const [region, setRegion] = useState("");
  const [tectonicTypes, setTectonicTypes] = useState([]);
  const [secretKey, setSecretKey] = useState("");
  const [secretKeyError, setSecretKeyError] = useState(false);
  const [unkownError, setUnknownError] = useState(false);
  const [addedRunSuccess, setAddedRunSuccess] = useState(false);
  const [cantAddRun, setCantAddRun] = useState(false);
  const [processingRun, setProcessingRun] = useState(false);

  const RunTypes = [{value: "Cybershake", label: "Cybershake"}, {value: "Historical", label: "Historical"}];
  const TectTypes = [{value: "Shallow Crustal", label: "Shallow Crustal"}, {
    value: "Volcanic",
    label: "Volcanic"
  }, {value: "Subduction", label: "Subduction"}];
  const GridSpacings = [{value: "100m", label: "100m"}, {value: "200m", label: "200m"}, {value: "400m", label: "400m"}]

  useEffect(() => {
    let error = false;
    // Checks each field for an Entry and if not then sets the error to True
    if (runName === "") {
      error = true;
    }
    if (dropboxFolder === "") {
      error = true;
    }
    if (runType === "") {
      error = true;
    }
    if (gridSpacing === "") {
      error = true;
    }
    if (region === "") {
      error = true;
    }
    if (tectonicTypes.length === 0) {
      error = true;
    }
    setCantAddRun(error);
  }, [runName, dropboxFolder, runType, gridSpacing, region, tectonicTypes]);

  const addRun = () => {
    // Send an API request to add the run
    let queryString = APIQueryBuilder({
      "run_name": runName,
      "dropbox_folder": dropboxFolder,
      "run_type": runType.value,
      "grid_spacing": gridSpacing.value,
      "region": region,
      "tectonic_types": tectonicTypes.map((tectonicType) => tectonicType.value),
      "secret_key": secretKey,
    });

    setProcessingRun(true);
    setSecretKeyError(false);
    setUnknownError(false);
    setCantAddRun(true);

    fetch(CONSTANTS.CS_API_URL + CONSTANTS.ADD_RUN_ENDPOINT + queryString, {
      method: "POST",
    }).then(async (response) => {
      console.log(response);
      if (!response.ok) {
        if (response.status === 401) {
          // Secret Key Incorrect
          setSecretKeyError(true);
          setProcessingRun(false);
          setCantAddRun(false);
        } else {
          // General unknown error
          setUnknownError(true);
          setProcessingRun(false);
          setCantAddRun(false);
        }
      } else {
        setSecretKeyError(false);
        setUnknownError(false);
        setProcessingRun(false);
        setCantAddRun(false);
        setAddedRunSuccess(true);
      }
    });
  }

  return (
    <div className="add-run-section">
      <div className="border form-section">
        <div className="add-run-form-label">Add a new run</div>
        <TextField className="add-run-text-field" label="Run Name" variant="outlined"
                   onChange={(e) => setRunName(e.target.value)}></TextField>
        <TextField className="add-run-text-field" label="Dropbox Folder" variant="outlined"
                   helperText={'Folder path to the run data on dropbox e.g. /home/Cybershake/v22p12'}
                   onChange={(e) => setDropboxFolder(e.target.value)}></TextField>
        <TextField className="add-run-text-field" label="Region" variant="outlined"
                   onChange={(e) => setRegion(e.target.value)}></TextField>
        <TextField className="add-run-text-field" label="Secrect Key" variant="outlined" error={secretKeyError}
                   helperText={secretKeyError ? "Invalid Key" : ""}
                   onChange={(e) => setSecretKey(e.target.value)}></TextField>
        <Select
          className="add-run-select-box"
          placeholder="Cybershake or Historical Run Type"
          options={RunTypes}
          onChange={(e) => setRunType(e)}
        ></Select>
        <Select
          className="add-run-select-box"
          placeholder="Grid spacing"
          options={GridSpacings}
          onChange={(e) => setGridSpacing(e)}
        ></Select>
        <Select
          className="add-run-select-box"
          placeholder="Tectonic Types"
          options={TectTypes}
          isMulti={true}
          onChange={(e) => setTectonicTypes(e)}
        ></Select>
        <div className="add-run-bottom-buttons">
          <Button
            variant="primary"
            size="lg"
            className="find-dataset-button"
            disabled={cantAddRun}
            onClick={addRun}
          >
            Add Run
          </Button>
          {processingRun && <div>
            <CircularProgress className="add-run-spinner"/>
            <Alert className="add-run-info" severity="info">Adding run to the database - you can safely leave this page
              and the run will be added to the dataset momentarily.</Alert>
          </div>}
          {unkownError &&
            <Alert className="add-run-info" severity="error">Unknown Error occurred - Please recheck entry data or try
              again later</Alert>}
          {addedRunSuccess && <Alert className="add-run-info" severity="success">Run added successfully</Alert>}
        </div>
      </div>
    </div>
  );
};

export default memo(AddRun);
