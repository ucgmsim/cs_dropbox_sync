import React, { useEffect, useState, memo, useRef } from "react";
import Select from "react-select";

import { Runs, InstallCard } from "components";
import * as CONSTANTS from "Constants";
import { MultiSelect } from "react-multi-select-component";

import "assets/Form.css";
import "assets/Popup.css";
import { Button } from "react-bootstrap";

const Form = ({openPopup}) => {
  // Filters
  const [availableGridSpacings, setAvailableGridSpacings] = useState([]);
  const [selectedGridSpacings, setSelectedGridSpacings] = useState([]);
  const [availableRunTypes, setAvailableRunTypes] = useState([]);
  const [selectedRunTypes, setSelectedRunType] = useState([]);
  const [availableTectonicTypes, setAvailableTectonicTypes] = useState([]);
  const [selectedTectonicTypes, setSelectedTectonicTypes] = useState([]);

  // Runs
  const [availableRuns, setAvailableRuns] = useState([]);
  const [shownRuns, setShownRuns] = useState([]);
  const [selectedRun, setSelectedRun] = useState([]);
  const [runData, setRunData] = useState([]);
  const [runDataLookup, setRunDataLookup] = useState({});
  const [selectedRunData, setSelectedRunData] = useState([]);

  // Download Section
  const [downloadAvailable, setDownloadAvailable] = useState(false);
  const [availableDataTypes, setAvailableDataTypes] = useState([]);
  const [selectedDataTypes, setSelectedDataTypes] = useState([]);
  const [availableFaults, setAvailableFaults] = useState([]);
  const [selectedFaults, setSelectedFaults] = useState([]);
  const [downloadLinks, setDownloadLinks] = useState([]);
  const [selectedTotalSize, setSelectedTotalSize] = useState(0);
  const textAreaRef = useRef(null);

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
          tempOptionArray.push({ value: value, label: value });
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
          tempOptionArray.push({ value: value, label: value });
        }
        setAvailableTectonicTypes(tempOptionArray);
      });
    }
  }, [availableTectonicTypes]);

  // Apply filters when they are changed
  useEffect(() => {
    console.log("Changing Shown Runs");
    let tempRunDataLookup = runDataLookup;
    const gridSpacings = selectedGridSpacings.map((spacing) => spacing.value);
    console.log(gridSpacings);
    // let tempShownRuns = Object.keys(tempRunDataLookup).filter((run_name) => {
    //   return gridSpacings.includes(tempRunDataLookup[run_name]["card_info"]["grid_spacing"]);
    // });
    const tempShownRuns = Object.keys(tempRunDataLookup).reduce((acc, run_name) => {
      if (gridSpacings.includes(tempRunDataLookup[run_name]["card_info"]["grid_spacing"])) {
        acc.push({
          key: run_name,
          value: run_name,
        });
      }
      return acc;
    }, []);
    console.log(tempShownRuns);
    // if (shownRuns.length > 0) {
    //   console.log(tempRunDataLookup["v22p4"]["card_info"]["grid_spacing"]);
    // }
    setShownRuns(tempShownRuns);
  }, [selectedGridSpacings, selectedRunTypes, selectedTectonicTypes]);

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
          tempOptionArray.push({ value: value, label: value });
        }
        setAvailableRuns(tempOptionArray);
        setShownRuns(tempOptionArray);
      });
    }
  }, [availableRuns]);

  // Change the download options when a run is selected
  useEffect(() => {
    if (selectedRun.length > 0) {
      if (Object.keys(runDataLookup).length > 0) {
        // Set the selected run data
        setSelectedRunData(runDataLookup[selectedRun[0]]);

        // Set Available Data Types Select Dropdown
        let tempOptionArray = [];
        for (const value of Object.values(
          runDataLookup[selectedRun[0]]["data_types"]
        )) {
          tempOptionArray.push({ value: value, label: value });
        }
        setAvailableDataTypes(tempOptionArray);
        // Set Available Faults Array
        tempOptionArray = [];
        for (const key of Object.keys(
          runDataLookup[selectedRun[0]]["faults"]
        )) {
          tempOptionArray.push({ value: key, label: key });
        }
        setAvailableFaults(tempOptionArray);
      } else {
        setAvailableDataTypes([]);
        setAvailableFaults([]);
      }
    }
  }, [selectedRun]);

  // Updates changes to file size shown when data types and faults change
  useEffect(() => {
    if (selectedDataTypes.length > 0 && selectedFaults.length > 0) {
      let files = getSelectedFiles();
      let totalBytes = 0;
      for (const file of files) {
        totalBytes += file["file_size"];
      }
      setSelectedTotalSize(totalBytes);
      setDownloadAvailable(true);
    } else {
      setDownloadAvailable(false);
      setSelectedTotalSize(0);
    }
  }, [selectedDataTypes, selectedFaults]);

  const getSelectedFiles = () => {
    // Gets the files that are selected based on the selected preferences
    // Get the strings of the selected data types
    const selectedDataTypeStrings = selectedDataTypes.map((item) => item.value);

    let files = [];
    // Loop over the selected Faults
    for (const fault of selectedFaults) {
      // Find the fault info in the selected run data
      const faultInfo = selectedRunData["faults"][fault.value];
      // Loop over each file in the faultInfo and check if it matches the selected data types
      for (const file of Object.keys(faultInfo)) {
        if (selectedDataTypeStrings.some((item) => file.includes(item))) {
          files.push(faultInfo[file]);
        }
      }
    }
    return files;
  };

  async function downloadFiles() {
    // Downloads the files selected
    let files = getSelectedFiles();
    const totalFiles = files.length;

    if (totalFiles === 1) {
      setDownloadLinks([]);
      const link = document.createElement("a");
      // Just download the single file by itself
      link.href = files[0]["download_link"];
      link.download =
        selectedRun +
        "_" +
        files[0]["download_link"].split("/").pop().split("?").shift();
      link.click();
      link.remove();
    } else {
      // Multiple files, but BB is one of them, so download them all separately using a download manager
      setDownloadLinks(files.map((file) => file.download_link));
      openPopup();
    }
  }

  const formatBytes = (bytes) => {
    if (bytes === 0) {
      return "0 B";
    }

    const sizes = ["B", "KB", "MB", "GB", "TB"];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    const formattedBytes = parseFloat((bytes / Math.pow(1024, i)).toFixed(1));

    return `${formattedBytes} ${sizes[i]}`;
  };

  const onSelectRun = (e) => {
    if (e[0][0].localeCompare(selectedRun[0])) {
      setSelectedRun(e[0]);
      setSelectedDataTypes([]);
      setSelectedFaults([]);
    }
  }

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
              value={selectedDataTypes}
              isDisabled={availableDataTypes.length === 0}
              onChange={(e) => setSelectedDataTypes(e)}
            ></Select>
          </div>
          <div className="col-4">
            <MultiSelect
              options={availableFaults}
              isDisabled={availableFaults.length === 0}
              value={selectedFaults}
              onChange={(e) => setSelectedFaults(e)}
              overrideStrings={{
                "allItemsAreSelected": "All faults",
                "selectSomeItems": "Select Faults"
              }}
            />
          </div>
        </div>
        <p>Selected total file size: {formatBytes(selectedTotalSize)}</p>
        <Button
          variant="primary"
          size="lg"
          disabled={!downloadAvailable}
          className="download-button"
          onClick={downloadFiles}
        >
          Download
        </Button>
        {downloadLinks.length > 0 && (
          <div>
            <Button
              variant="primary"
              size="sm"
              className="download-button"
              onClick={openPopup}
            >
              Show Download Instructions
            </Button>

            <textarea
              ref={textAreaRef}
              value={downloadLinks.join("\n")}
              readOnly
              style={{ position: "absolute", left: "-9999px" }}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default memo(Form);
