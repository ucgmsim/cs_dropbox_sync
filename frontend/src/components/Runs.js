import React, { useEffect, useState, memo } from "react";
import { Card, Placeholder } from "react-bootstrap";

import * as CONSTANTS from "Constants";

import "assets/Runs.css";

const Runs = ({ viewRuns, runData, setRun }) => {
  const [loadedRunData, setLoadedRunData] = useState([]);

  // Update when the runData changes
  useEffect(() => {
    console.log("Run Data Changed");
    // Only update if the runData length has changed
    if (runData.length !== loadedRunData.length) {
      console.log("Updating Run Data");
      // Convert the runData array into a lookup table
      const runDataLookup = runData.reduce((lookup, run) => {
        lookup[Object.keys(run)[0]] = Object.values(run)[0];
        return lookup;
      }, {});
      setLoadedRunData(runDataLookup);
    }
  }, [runData]);

  const loadingPlaceholder = (
    <Placeholder as={Card.Text} animation="glow" xs={12}>
      <Placeholder xs={8} size={"sm"} bg="secondary" />{" "}
      <Placeholder xs={3} size={"sm"} bg="secondary" />
      <Placeholder xs={5} size={"sm"} bg="secondary" />{" "}
      <Placeholder xs={6} size={"sm"} bg="secondary" />
      <Placeholder xs={7} size={"sm"} bg="secondary" />{" "}
      <Placeholder xs={4} size={"sm"} bg="secondary" />
      <Placeholder xs={8} size={"sm"} bg="secondary" />{" "}
      <Placeholder xs={3} size={"sm"} bg="secondary" />
      <Placeholder xs={7} size={"sm"} bg="secondary" />{" "}
      <Placeholder xs={4} size={"sm"} bg="secondary" />
    </Placeholder>
  );

  if (viewRuns.length > 0) {
    return (
      <div className="sub-section run-card-holder">
        {viewRuns.map(function (run, i) {
          return (
            <Card className="run-card" key={i}>
              <Card.Body className="run-card-body">
                <Card.Title className="run-card-title">{run.value}</Card.Title>
                {loadedRunData[run.value] && (
                  <Card.Text className="run-card-info-text">
                    <b>Number of Faults:</b> {loadedRunData[run.value]["card_info"]["n_faults"]}
                    <br />
                    <b>Region:</b> {loadedRunData[run.value]["card_info"]["region"]}
                    <br />
                    <b>Grid Spacing:</b> {loadedRunData[run.value]["card_info"]["grid_spacing"]}
                    <br />
                    <b>Scientific Version:</b> {
                      loadedRunData[run.value]["card_info"][
                        "scientific_version"
                      ]
                    }
                    <br />
                    <b>Tectonic Types:</b> {loadedRunData[run.value]["card_info"]["tectonic_types"].join(', ')}
                  </Card.Text>
                )}
                {!loadedRunData[run.value] && loadingPlaceholder}
              </Card.Body>
            </Card>
          );
        })}
      </div>
    );
  } else {
    return (
      <div className="sub-section run-card-holder">
        {/* Loops a demo loading card 9 times */}
        {Array.from(Array(9), (e, i) => {
          return (
            <Card className="run-card" key={i}>
              <Card.Body className="run-card-body">
                <Card.Title className="run-card-title">
                  <Placeholder as={Card.Title} animation="glow" xs={12}>
                    <Placeholder xs={12} size={"lg"} bg="secondary" />{" "}
                  </Placeholder>
                </Card.Title>
                {loadingPlaceholder}
              </Card.Body>
            </Card>
          );
        })}
      </div>
    );
  }
};

export default memo(Runs);
