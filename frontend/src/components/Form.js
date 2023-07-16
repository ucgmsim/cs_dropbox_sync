import React, { useEffect, useState, memo } from "react";
import Select from "react-select";

import { Runs } from "components";
import * as CONSTANTS from "Constants";

import "assets/Form.css";
import { Button, ProgressBar } from "react-bootstrap";
import { APIQueryBuilder } from "./Utils";
import { downloadZip } from "https://cdn.jsdelivr.net/npm/client-zip/index.js";

const Form = () => {
  // Filters
  const [availableGridSpacings, setAvailableGridSpacings] = useState([]);
  const [selectedGridSpacings, setSelectedGridSpacings] = useState([]);
  const [availableScientificVersions, setAvailableScientificVersions] =
    useState([]);
  const [selectedScientificVersions, setSelectedScientificVersions] = useState(
    []
  );
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
  const [availableDataTypes, setAvailableDataTypes] = useState([]);
  const [selectedDataTypes, setSelectedDataTypes] = useState([]);
  const [availableFaults, setAvailableFaults] = useState([]);
  const [selectedFaults, setSelectedFaults] = useState([]);
  const [formattedRemainingTime, setFormattedRemainingTime] = useState(null);
  const [progress, setProgress] = useState(0);
  const [progressWidth, setProgressWidth] = useState(0);

  const FileSaver = require('file-saver');

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
    if (Object.keys(runData).length === 0) {
      // Get the run data for all the runs
      fetch(CONSTANTS.CS_API_URL + CONSTANTS.GET_RUNS_INFO_ENDPOINT, {
        method: "GET",
      }).then(async (response) => {
        const responseData = await response.json();
        setRunData(responseData);
      });
    }
  }, [availableRuns]);

  // Update when the runData changes
  useEffect(() => {
    // Only update if the runData length has changed
    if (runData.length !== Object.keys(runDataLookup).length) {
      // Convert the runData array into a lookup table
      const runDataLookupTemp = runData.reduce((lookup, run) => {
        lookup[Object.keys(run)[0]] = Object.values(run)[0];
        return lookup;
      }, {});
      setRunDataLookup(runDataLookupTemp);
    }
  }, [runData]);

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

  const onSelectGridSpacing = (e) => {
    setSelectedGridSpacings(e);
  };

  const onSelectScientificVersion = (e) => {
    setSelectedScientificVersions(e);
  };

  const onSelectTectonicType = (e) => {
    setSelectedTectonicTypes(e);
  };

  const downloadData = () => {
    // Downloads the data based on the selected preferences
    // Get the strings of the selected data types
    const selectedDataTypeStrings = selectedDataTypes.map((item) => item.value);

    let delay = 0;
    let urls = [];
    // Loop over the selected Faults
    for (const fault of selectedFaults) {
      // Find the fault info in the selected run data
      const faultInfo = selectedRunData["faults"][fault.value];
      // Loop over each file in the faultInfo and check if it matches the selected data types
      for (const file of Object.keys(faultInfo)) {
        if (selectedDataTypeStrings.some((item) => file.includes(item))) {
          urls.push(faultInfo[file]);
        }
      }
    }
    downloadAndZipFiles(urls);
  };

  async function downloadAndZipFiles(files) {
    // Downloads and zips the given files
    const zipFiles = [];
  
    const totalFiles = files.length;
    let completedFiles = 0;
    let totalBytes = 0;
    let downloadedBytes = 0;
    let startTime = new Date();
    let averageDownloadSpeed = 14926; // Based on an average calculated before
    let remainingTime = 0;
    let cur_file_size = files[0]["file_size"];
    let currentStepTime = startTime;

    // Set the progress bar to 0
    setProgress(0);

    // Calculate totalBytes
    for (const file of files) {
      totalBytes += file["file_size"];
    }

    const updateRemainingTime = () => {
      const currentTime = new Date();
      const elapsedTime = currentTime - startTime; // Time in milliseconds
      const remainingBytes = totalBytes - (elapsedTime * averageDownloadSpeed);
      remainingTime = remainingBytes / averageDownloadSpeed;

      // Update the progress bar
      let current_step = Math.round((completedFiles / totalFiles) * 100);
      let next_step = Math.round(((completedFiles + 1) / totalFiles) * 100);
      let estimated_completion = Math.min(averageDownloadSpeed * (currentTime- currentStepTime) / cur_file_size, 1);
      setProgress(Math.round(current_step + (next_step - current_step) * estimated_completion));
      console.log(current_step);
      console.log(next_step);
      console.log(estimated_completion);
  
      // Format the remaining time based on different units
      if (remainingTime < 60000) {
        setFormattedRemainingTime((remainingTime / 1000).toFixed(1) + ' seconds');
      } else if (remainingTime < 3600000) {
        const minutes = Math.floor(remainingTime / 60000);
        const seconds = Math.floor((remainingTime % 60000) / 1000);
        setFormattedRemainingTime(minutes + ' minutes ' + seconds + ' seconds');
      } else {
        const hours = Math.floor(remainingTime / 3600000);
        const minutes = Math.floor((remainingTime % 3600000) / 60000);
        setFormattedRemainingTime(hours + ' hours ' + minutes + ' minutes');
      }
    };

    let updateInterval = setInterval(updateRemainingTime, 1000); // Update every 1 second
  
    for (const file of files) {
      const url = file["download_link"];
      const file_size = file["file_size"];
      cur_file_size = file_size;
      const filename = url.split('/').pop().split("?").shift();
  
      console.log("Downloading file: " + url);
      const response = await fetch(url);
      const content = await response.text();
      console.log("Downloaded file: " + url);
  
      downloadedBytes += file_size;
      const zipFile = {
        name: filename,
        lastModified: new Date(),
        input: content
      };
      zipFiles.push(zipFile);
      console.log("Zipped file: " + url);
  
      completedFiles++;
      setProgress(Math.round((completedFiles / totalFiles) * 100));
  
      currentStepTime = new Date();
      const elapsedTime = currentStepTime - startTime; // Time in milliseconds
      averageDownloadSpeed = downloadedBytes / elapsedTime; // Update average download speed
      console.log("Average download speed: " + averageDownloadSpeed + " bytes per millisecond");
  
      clearInterval(updateInterval); // Clear the interval before updating remainingTime
      updateRemainingTime(); // Update remainingTime immediately after file download
      updateInterval = setInterval(updateRemainingTime, 1000); // Resume the interval
    }
  
    clearInterval(updateInterval); 
  
    // Generate the ZIP blob
    let downloadStart = new Date();
    const zipBlob = await downloadZip(zipFiles).blob();

    const link = document.createElement("a");
    link.href = URL.createObjectURL(zipBlob);
    link.download = selectedRun + '.zip';
    link.click();
    link.remove();
    console.log("Time taken for zip compression: " + (new Date() - downloadStart) + " milliseconds");
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
        <div className="border run-cards-section">
          <Runs
            viewRuns={shownRuns}
            runData={runDataLookup}
            setRun={setSelectedRun}
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
        <Button
          variant="primary"
          size="lg"
          className="download-button"
          onClick={downloadData}
        >
          Download
        </Button>
        <ProgressBar now={progress} label={`${progress}%`} animated striped />
        {/* <div
        style={{
          width: '100%',
          height: '20px',
          backgroundColor: '#eee',
          borderRadius: '10px',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            width: `${progressWidth}%`,
            height: '100%',
            backgroundColor: '#007bff',
            transition: 'width 300ms ease-in-out',
          }}
        />
      </div> */}
      <p>Estimated Time Remaining: {formattedRemainingTime}</p>
      </div>
    </div>
  );
};

export default memo(Form);
