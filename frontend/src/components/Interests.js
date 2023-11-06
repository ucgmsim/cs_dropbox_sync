import React, { useEffect, useState, memo, } from "react";
import Select from "react-select";
import AsyncSelect from 'react-select/async';

import * as CONSTANTS from "Constants";

import "assets/Interests.css";
import "assets/Popup.css";
import { Button } from "react-bootstrap";

const Interests = ({setInterest}) => {
  const [selectedSiteOrSource, setSiteOrSource] = useState(null);
  const [selectedSites, setSelectedSites] = useState([]);
  const [selectedSources, setSelectedSources] = useState([]);
  const [availableSites, setAvailableSites] = useState([]);
  const [availableSources, setAvailableSources] = useState([]);

  const siteSourceOptions = [{ value: "Site", label: "Site" }, { value: "Source", label: "Source" }];

  // Get Available Sources on page load
  useEffect(() => {
    if (availableSources.length === 0) {
      fetch(CONSTANTS.CS_API_URL + CONSTANTS.GET_UNIQUE_FAULTS_ENDPOINT, {
        method: "GET",
      }).then(async (response) => {
        const responseData = await response.json();
        // Set Available Faults for the Select Dropdown
        let tempOptionArray = [];
        for (const value of Object.values(responseData)) {
          tempOptionArray.push({ value: value, label: value });
        }
        setAvailableSources(tempOptionArray);
      });
    }
  }, [availableSources]);

  // Get Available Sites on page load
  useEffect(() => {
    if (availableSites.length === 0) {
      fetch(CONSTANTS.CS_API_URL + CONSTANTS.GET_UNIQUE_SITES_ENDPOINT, {
        method: "GET",
      }).then(async (response) => {
        const responseData = await response.json();
        // Set Available Sites for the Select Dropdown
        let tempOptionArray = [];
        for (const value of Object.values(responseData)) {
          tempOptionArray.push({ value: value, label: value });
        }
        setAvailableSites(tempOptionArray);
      });
    }
  }, [availableSites]);

  const findDataset = () => {
    setInterest(selectedSites, selectedSources);
  }

  const skipAndBrowseDatasets = () => {
    // setInterest([{"sites": []}], [{"sources": []}]);
    setInterest([], []);
  }

  const filterColors = (inputValue) => {
    return availableSites.filter((i) =>
      i.label.toLowerCase().includes(inputValue.toLowerCase())
    );
  };

  const promiseOptions = (inputValue) =>
    new Promise((resolve) => {
      setTimeout(() => {
        resolve(filterColors(inputValue));
      }, 1000);
    });

  return (
    <div className="border section">
      <div className="sub-section-interests">
        <div className="form-label">Do you have a Site or Source of interest?</div>
        <Select
          className="site-source-select-box"
          placeholder="Site or Source"
          options={siteSourceOptions}
          onChange={(e) => setSiteOrSource(e)}
        ></Select>
        {selectedSiteOrSource !== null && selectedSiteOrSource.value === "Site" && (
          <AsyncSelect
            className="site-source-select-box"
            isMulti
            cacheOptions
            onChange={(e) => setSelectedSites(e)}
            loadOptions={promiseOptions}
          />
        )}
        {selectedSiteOrSource !== null && selectedSiteOrSource.value === "Source" && (
          <Select
            className="site-source-select-box"
            placeholder="Source"
            isMulti={true}
            options={availableSources}
            onChange={(e) => setSelectedSources(e)}
          ></Select>
        )}
        <div className="bottom-buttons">
          <Button
            variant="primary"
            size="lg"
            className="find-dataset-button"
            onClick={findDataset}
            disabled={selectedSites.length === 0 && selectedSources.length === 0}
          >
            Find Dataset
          </Button>
          <Button
            variant="secondary"
            className="find-dataset-button"
            onClick={skipAndBrowseDatasets}
          >
            Skip and Browse Datasets
          </Button>
        </div>
      </div>
    </div>
  );
};

export default memo(Interests);
