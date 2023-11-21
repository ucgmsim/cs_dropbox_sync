import React, {useEffect, useState, memo} from "react";
import Select from "react-select";

import {Runs} from "components";
import * as CONSTANTS from "Constants";
import Alert from '@mui/material/Alert';

import "assets/Form.css";
import "assets/Popup.css";
import {Button} from "react-bootstrap";
import {APIQueryBuilder} from "./Utils";

const Form = ({interests, setDataset, goBack}) => {
  // Filters
  const [availableGridSpacings, setAvailableGridSpacings] = useState([]);
  const [selectedGridSpacings, setSelectedGridSpacings] = useState([]);
  const [availableRunTypes, setAvailableRunTypes] = useState([]);
  const [selectedRunTypes, setSelectedRunType] = useState([]);
  const [availableTectonicTypes, setAvailableTectonicTypes] = useState([]);
  const [selectedTectonicTypes, setSelectedTectonicTypes] = useState([]);
  const [siteOrSourceText, setSiteOrSourceText] = useState("");

  // Filter Runs
  const [interestRuns, setInterestRuns] = useState(null);
  const [GridSpacingRuns, setGridSpacingRuns] = useState(null);
  const [RunTypeRuns, setRunTypeRuns] = useState(null);
  const [TectonicTypeRuns, setTectonicTypeRuns] = useState(null);

  // Runs
  const [availableRuns, setAvailableRuns] = useState([]);
  const [shownRuns, setShownRuns] = useState([]);
  const [selectedRun, setSelectedRun] = useState([]);
  const [runData, setRunData] = useState([]);
  const [runDataLookup, setRunDataLookup] = useState({});
  const [selectedRunData, setSelectedRunData] = useState([]);

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
          tempOptionArray.push({value: value, label: value});
        }
        setAvailableGridSpacings(tempOptionArray);
      });
    }
  }, [availableGridSpacings]);

  // Get Run Type filter on page load
  useEffect(() => {
    if (availableRunTypes.length === 0) {
      fetch(CONSTANTS.CS_API_URL + CONSTANTS.GET_RUN_TYPES_ENDPOINT, {
        method: "GET",
      }).then(async (response) => {
        const responseData = await response.json();
        // Set Available Run Types for the Select Dropdown
        let tempOptionArray = [];
        for (const value of Object.values(responseData)) {
          tempOptionArray.push({value: value, label: value});
        }
        setAvailableRunTypes(tempOptionArray);
      });
    }
  }, [availableRunTypes]);

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
          tempOptionArray.push({value: value, label: value});
        }
        setAvailableTectonicTypes(tempOptionArray);
      });
    }
  }, [availableTectonicTypes]);

  // Function to apply every filter to the available runs to set the shown runs
  useEffect(() => {
    // Add every set together, if null ignore
    let tempShownRuns = availableRuns;
    if (interestRuns !== null) {
      tempShownRuns = interestRuns.filter(interestRun =>
        tempShownRuns.some(tempShownRun => interestRun.value === tempShownRun.value)
      );
    }
    if (GridSpacingRuns !== null) {
      tempShownRuns = GridSpacingRuns.filter(gridSpacingRun =>
        tempShownRuns.some(tempShownRun => gridSpacingRun.value === tempShownRun.value)
      );
    }
    if (RunTypeRuns !== null) {
      tempShownRuns = RunTypeRuns.filter(runTypeRun =>
        tempShownRuns.some(tempShownRun => runTypeRun.value === tempShownRun.value)
      );
    }
    if (TectonicTypeRuns !== null) {
      tempShownRuns = TectonicTypeRuns.filter(tectonicTypeRun =>
        tempShownRuns.some(tempShownRun => tectonicTypeRun.value === tempShownRun.value)
      );
    }
    setShownRuns(tempShownRuns);
  }, [availableRuns, interestRuns, GridSpacingRuns, RunTypeRuns, TectonicTypeRuns]);

  // Set GridSpacingRuns when the Grid Spacing filter is changed
  useEffect(() => {
    if (selectedGridSpacings.length > 0) {
      let tempRunDataLookup = runDataLookup;
      const gridSpacings = selectedGridSpacings.map((spacing) => spacing.value);
      const tempShownRuns = Object.keys(tempRunDataLookup).reduce((acc, run_name) => {
        if (gridSpacings.includes(tempRunDataLookup[run_name]["card_info"]["grid_spacing"])) {
          acc.push({
            key: run_name,
            value: run_name,
          });
        }
        return acc;
      }, []);
      setGridSpacingRuns(tempShownRuns);
    } else {
      setGridSpacingRuns(null);
    }
  }, [runDataLookup, selectedGridSpacings]);

  // Set RunTypeRuns when the Run Type filter is changed
  useEffect(() => {
    if (selectedRunTypes.length > 0) {
      let tempRunDataLookup = runDataLookup;
      const runTypes = selectedRunTypes.map((runType) => runType.value);
      const tempShownRuns = Object.keys(tempRunDataLookup).reduce((acc, run_name) => {
        if (runTypes.includes(tempRunDataLookup[run_name]["card_info"]["run_type"])) {
          acc.push({
            key: run_name,
            value: run_name,
          });
        }
        return acc;
      }, []);
      setRunTypeRuns(tempShownRuns);
    } else {
      setRunTypeRuns(null);
    }
  }, [runDataLookup, selectedRunTypes]);

  // Set TectonicTypeRuns when the Tectonic Type filter is changed
  useEffect(() => {
    if (selectedTectonicTypes.length > 0) {
      let tempRunDataLookup = runDataLookup;
      const tectonicTypes = selectedTectonicTypes.map((tectonicType) => tectonicType.value);
      const tempShownRuns = Object.keys(tempRunDataLookup).reduce((acc, run_name) => {
        // Loop over each tectonic type in the run
        for (const tectonicType of tempRunDataLookup[run_name]["card_info"]["tectonic_types"]) {
          if (tectonicTypes.includes(tectonicType)) {
            acc.push({
              key: run_name,
              value: run_name,
            });
            break;
          }
        }
        return acc;
      }, []);
      setTectonicTypeRuns(tempShownRuns);
    } else {
      setTectonicTypeRuns(null);
    }
  }, [runDataLookup, selectedTectonicTypes]);

  // Get Available Runs on page load
  useEffect(() => {
    if (Object.keys(runData).length === 0) {
      // Get the run data for all the runs
      fetch(CONSTANTS.CS_API_URL + CONSTANTS.GET_RUNS_INFO_ENDPOINT, {
        method: "GET",
      }).then(async (response) => {
        const responseData = await response.json();
        setRunData(responseData);
        const runDataLookupTemp = responseData.reduce((lookup, run) => {
          lookup[Object.keys(run)[0]] = Object.values(run)[0];
          return lookup;
        }, {});
        setRunDataLookup(runDataLookupTemp);
        // Set Available Runs Array
        let tempOptionArray = [];
        for (const run_dict of Object.values(responseData)) {
          const value = Object.keys(run_dict)[0];
          tempOptionArray.push({value: value, label: value});
        }
        setAvailableRuns(tempOptionArray);
      });
    }
  }, [runData]);

  // Set the Interests text based on the interests selected
  useEffect(() => {
    // Find if the interests are Sites or sources
    let tmpSiteOrSourceText = "";
    let filterBy = "";
    let filteredList = [];
    if (interests[0]["sites"].length > 0) {
      tmpSiteOrSourceText = "Filtered by Sites of Interest (";
      for (const site of interests[0]["sites"]) {
        tmpSiteOrSourceText += site["value"] + ", ";
        filteredList.push(site["value"]);
      }
      tmpSiteOrSourceText += ")";
      filterBy = "sites";
    } else if (interests[1]["sources"].length > 0) {
      tmpSiteOrSourceText = "Filtered by Sources of Interest (";
      for (const source of interests[1]["sources"]) {
        tmpSiteOrSourceText += source["value"] + ", ";
        filteredList.push(source["value"]);
      }
      tmpSiteOrSourceText += ")";
      filterBy = "sources";
    } else {
      // There is no Interests
      tmpSiteOrSourceText = null;
    }
    setSiteOrSourceText(tmpSiteOrSourceText);
    if (tmpSiteOrSourceText !== null) {
      let queryString = APIQueryBuilder({
        filter_by: filterBy,
        filter_list: filteredList,
      });

      // Send a request to the API to get the runs that match the interests
      fetch(CONSTANTS.CS_API_URL + CONSTANTS.GET_RUNS_FROM_INTERESTS_ENDPOINT + queryString, {
        method: "GET",
      }).then(async (response) => {
        const responseData = await response.json();
        // Set Shown Runs Array
        let tempOptionArray = [];
        for (const value of Object.values(responseData)) {
          tempOptionArray.push({value: value, label: value});
        }
        setInterestRuns(tempOptionArray);
      });
    }
  }, [interests]);

  // Change the download options when a run is selected
  useEffect(() => {
    if (selectedRun.length > 0) {
      if (Object.keys(runDataLookup).length > 0) {
        // Set the selected run data
        setSelectedRunData(runDataLookup[selectedRun[0]]);
      }
    }
  }, [runDataLookup, selectedRun]);

  const onSelectRun = (e) => {
    if (e[0][0].localeCompare(selectedRun[0])) {
      setSelectedRun(e[0]);
    }
  }

  const selectDataset = () => {
    setDataset(selectedRun, selectedRunData);
  }

  const removeInterestFilter = () => {
    setInterestRuns(null);
    setSiteOrSourceText(null);
  }

  return (
    <div className="border section">
      <div className="sub-section">
        {siteOrSourceText !== null && <Alert
          severity="info"
          action={
            <Button variant="secondary"
                    size="sm" onClick={removeInterestFilter}>
              Remove Filter
            </Button>
          }
        >
          {siteOrSourceText}
        </Alert>
        }
        <div className="form-label">Filters</div>
        <div className="row three-column-row">
          <div className="col-4">
            <Select
              className="select-box"
              placeholder="Grid Spacing"
              isMulti={true}
              options={availableGridSpacings}
              isDisabled={availableGridSpacings.length === 0}
              onChange={(e) => setSelectedGridSpacings(e)}
            ></Select>
          </div>
          <div className="col-4">
            <Select
              className="select-box"
              placeholder="Run Type"
              isMulti={true}
              options={availableRunTypes}
              isDisabled={availableRunTypes.length === 0}
              onChange={(e) => setSelectedRunType(e)}
            ></Select>
          </div>
          <div className="col-4">
            <Select
              className="select-box"
              placeholder="Tectonic Types"
              isMulti={true}
              options={availableTectonicTypes}
              isDisabled={availableTectonicTypes.length === 0}
              onChange={(e) => setSelectedTectonicTypes(e)}
            ></Select>
          </div>
        </div>
      </div>
      <div className="sub-section">
        <div className="border run-cards-section">
          <Runs
            viewRuns={shownRuns}
            runData={runDataLookup}
            setRun={onSelectRun}
          />
        </div>
        <Button
          variant="primary"
          size="lg"
          disabled={selectedRun.length === 0}
          className="select-dataset-button"
          onClick={selectDataset}
        >
          Select Dataset
        </Button>
      </div>
      <div className="nav-section">
        <Button
          variant="secondary"
          size="sm"
          className="back-button"
          onClick={goBack}
        >
          Back
        </Button>
      </div>

    </div>
  );
};

export default memo(Form);
