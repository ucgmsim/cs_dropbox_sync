import React, { useEffect, useState, memo } from "react";
import Select from "react-select";

import { Runs } from "components";
import * as CONSTANTS from "Constants";

import "assets/Form.css";
import { Button } from "react-bootstrap";

const Form = () => {
  // Filters
  const [availableGridSpacings, setAvailableGridSpacings] = useState([]);
  const [selectedGridSpacings, setSelectedGridSpacings] = useState([]);
  const [availableScientificVersions, setAvailableScientificVersions] = useState([]);
  const [selectedScientificVersions, setSelectedScientificVersions] = useState([]);
  const [availableTectonicTypes, setAvailableTectonicTypes] = useState([]);
  const [selectedTectonicTypes, setSelectedTectonicTypes] = useState([]);

  // Runs
  const [availableRuns, setAvailableRuns] = useState([]);
  const [shownRuns, setShownRuns] = useState(["1", "2"]);
  const [selectedRun, setSelectedRun] = useState([]);
  const [runData, setRunData] = useState([]);
  const [selectedRunData, setSelectedRunData] = useState([]);

  // Download Section
  const [availableDataTypes, setAvailableDataTypes] = useState([]);
  const [selectedDataTypes, setSelectedDataTypes] = useState([]);
  const [availableFaults, setAvailableFaults] = useState([]);
  const [selectedFaults, setSelectedFaults] = useState([]);

  // Get Grid Spacing filter on page load
  useEffect(() => {
    if (availableGridSpacings.length === 0) {
      fetch(CONSTANTS.CS_API_URL + CONSTANTS.GET_GRID_SPACING_ENDPOINT, {
        method: "GET",
      }).then(async (response) => {
        const responseData = await response.json();
        // Set Available Grid Spacing Select Dropdown
        let tempOptionArray = [];
        for (const value of Object.values(responseData)) {
          tempOptionArray.push({ value: value, label: value });
        }
        setAvailableGridSpacings(tempOptionArray);
      });
    }
  }, [availableGridSpacings]);

  // Get Scientific Version filter on page load
  useEffect(() => {
    if (availableScientificVersions.length === 0) {
      fetch(CONSTANTS.CS_API_URL + CONSTANTS.GET_SCIENTIFIC_VERSION_ENDPOINT, {
        method: "GET",
      }).then(async (response) => {
        const responseData = await response.json();
        // Set Available Scientific Version Select Dropdown
        let tempOptionArray = [];
        for (const value of Object.values(responseData)) {
          tempOptionArray.push({ value: value, label: value });
        }
        setAvailableScientificVersions(tempOptionArray);
      });
    }
  }, [availableScientificVersions]);


  // Get Tectonic Types filter on page load
  useEffect(() => {
    if (availableTectonicTypes.length === 0) {
      fetch(CONSTANTS.CS_API_URL + CONSTANTS.GET_TECTONIC_TYPES_ENDPOINT, {
        method: "GET",
      }).then(async (response) => {
        const responseData = await response.json();
        // Set Available Tectonic Types Select Dropdown
        let tempOptionArray = [];
        for (const value of Object.values(responseData)) {
          tempOptionArray.push({ value: value, label: value });
        }
        setAvailableTectonicTypes(tempOptionArray);
      });
    }
  }, [availableTectonicTypes]);

  // Get Data Types on page load
  useEffect(() => {
    if (availableDataTypes.length === 0) {
      fetch(CONSTANTS.CS_API_URL + CONSTANTS.GET_DATA_TYPES_ENDPOINT, {
        method: "GET",
      }).then(async (response) => {
        const responseData = await response.json();
        // Set Available Data Types Select Dropdown
        let tempOptionArray = [];
        for (const value of Object.values(responseData)) {
          tempOptionArray.push({ value: value, label: value });
        }
        setAvailableDataTypes(tempOptionArray);
      });
    }
  }, [availableDataTypes]);

  // Get Available Runs on page load
  useEffect(() => {
    if (availableRuns.length === 0) {
      fetch(CONSTANTS.CS_API_URL + CONSTANTS.GET_AVAILABLE_RUNS_ENDPOINT, {
        method: "GET",
      }).then(async (response) => {
        const responseData = await response.json();
        // Set Available Runs Array
        let tempOptionArray = [];
        for (const value of Object.values(responseData)) {
          tempOptionArray.push({ value: value, label: value });
        }
        setAvailableRuns(tempOptionArray);
        setShownRuns(tempOptionArray);
      });
    }
  }, [availableRuns]);

  const onSelectGridSpacing = (e) => {
    setSelectedGridSpacings(e);
  };

  const onSelectScientificVersion = (e) => {
    setSelectedScientificVersions(e);
  };

  const onSelectTectonicType = (e) => {
    setSelectedTectonicTypes(e);
  };

  return (
    <div className="border section">
      <div className="sub-section">
        <div className="form-label">Filters</div>
        <div className="row three-column-row">
          <div className="col-4">
            <Select
              className="select-box"
              placeholder="Grid Spacing"
              isMulti={true}
              options={availableGridSpacings}
              isDisabled={availableGridSpacings.length === 0}
              onChange={(e) => onSelectGridSpacing(e)}
            ></Select>
          </div>
          <div className="col-4">
            <Select
              className="select-box"
              placeholder="Scientific Version"
              isMulti={true}
              options={availableScientificVersions}
              isDisabled={availableScientificVersions.length === 0}
              onChange={(e) => onSelectScientificVersion(e)}
            ></Select>
          </div>
          <div className="col-4">
            <Select
              className="select-box"
              placeholder="Tectonic Types"
              isMulti={true}
              options={availableTectonicTypes}
              isDisabled={availableTectonicTypes.length === 0}
              onChange={(e) => onSelectTectonicType(e)}
            ></Select>
          </div>
        </div>
      </div>
      <div className="sub-section">
        <Runs
          viewRuns={shownRuns}
          runData={runData}
          setRun={setSelectedRun}
        />
      </div>
      <div className="sub-section">
        <div className="form-label">Download Data</div>
        <div className="row two-column-row center-elm">
          <div className="col-4">
            <Select
              className="select-box"
              placeholder="Data Types"
              isMulti={true}
              options={availableDataTypes}
              isDisabled={availableDataTypes.length === 0}
              onChange={(e) => setSelectedDataTypes(e)}
            ></Select>
          </div>
          <div className="col-4">
            <Select
              className="select-box"
              placeholder="Faults"
              isMulti={true}
              options={availableFaults}
              isDisabled={availableFaults.length === 0}
              onChange={(e) => setSelectedFaults(e)}
            ></Select>
          </div>
        </div>
        <Button variant="primary" size="lg" className="download-button">
          Download
        </Button>
      </div>
    </div>
  );
};

export default memo(Form);
