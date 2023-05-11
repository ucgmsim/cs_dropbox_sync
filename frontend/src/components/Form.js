import React, { useEffect, useState, memo } from "react";
import Select from "react-select";

import * as CONSTANTS from "Constants";

import "assets/App.css";

const Form = () => {
  // Dropbox Data
  const [availableRuns, setAvailableRuns] = useState([]);
  const [selectedRuns, setSelectedRuns] = useState([]);

  // Get Available Runs on page load
  useEffect(() => {
    if (availableRuns.length === 0) {
      fetch(CONSTANTS.CS_API_URL + CONSTANTS.GET_AVAILABLE_RUNS_ENDPOINT, {
        method: "GET",
      }).then(async (response) => {
        const responseData = await response.json();
        // Set Available Runs Select Dropdown
        let tempOptionArray = [];
        for (const value of Object.values(responseData)) {
          tempOptionArray.push({ value: value, label: value });
        }
        setAvailableRuns(tempOptionArray);
      });
    }
  }, []);

  const onSelectRuns = (e) => {
    setSelectedRuns(e);
  };

  return (
    <div className="center-elm">
      <Select
        className="select-box"
        placeholder="Select Cybershake Runs"
        isMulti={true}
        options={availableRuns}
        isDisabled={availableRuns.length === 0}
        onChange={(e) => onSelectRuns(e)}
      ></Select>
    </div>
  );
};

export default memo(Form);
