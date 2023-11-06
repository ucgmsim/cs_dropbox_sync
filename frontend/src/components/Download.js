import React, {useEffect, useState, memo, useRef} from "react";
import Select from "react-select";

import {MultiSelect} from "react-multi-select-component";

import "assets/Download.css";
import "assets/Popup.css";
import {Button} from "react-bootstrap";

const Download = ({openPopup, selectedRunData, selectedRun, goBack}) => {
  const [downloadAvailable, setDownloadAvailable] = useState(false);
  const [availableDataTypes, setAvailableDataTypes] = useState([]);
  const [selectedDataTypes, setSelectedDataTypes] = useState([]);
  const [availableFaults, setAvailableFaults] = useState([]);
  const [selectedFaults, setSelectedFaults] = useState([]);
  const [downloadLinks, setDownloadLinks] = useState([]);
  const [selectedTotalSize, setSelectedTotalSize] = useState(0);
  const textAreaRef = useRef(null);

  // Get Data Types filter on page load
  useEffect(() => {
    // Set Available Data Types Select Dropdown
    let tempOptionArray = [];
    for (const value of Object.values(
      selectedRunData["data_types"]
    )) {
      tempOptionArray.push({value: value, label: value});
    }
    setAvailableDataTypes(tempOptionArray);
    // Set Available Faults Array
    tempOptionArray = [];
    for (const key of Object.keys(
      selectedRunData["faults"]
    )) {
      tempOptionArray.push({value: key, label: key});
    }
    setAvailableFaults(tempOptionArray);
  }, []);

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

  const formatBytes = (bytes) => {
    if (bytes === 0) {
      return "0 B";
    }

    const sizes = ["B", "KB", "MB", "GB", "TB"];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    const formattedBytes = parseFloat((bytes / Math.pow(1024, i)).toFixed(1));

    return `${formattedBytes} ${sizes[i]}`;
  };

  return (
    <div className="border section">
      <div className="sub-section">
        <div className="form-label">Download Data</div>
        <div className="download-selects">
          <Select
            className="download-select-box"
            placeholder="Data Types"
            isMulti={true}
            options={availableDataTypes}
            value={selectedDataTypes}
            isDisabled={availableDataTypes.length === 0}
            onChange={(e) => setSelectedDataTypes(e)}
          ></Select>
          <MultiSelect
            className="download-select-box"
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
              variant="secondary"
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
              style={{position: "absolute", left: "-9999px"}}
            />
          </div>
        )}
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

export default memo(Download);