import React, { useEffect, useState, memo } from "react";
import { Card, Placeholder } from "react-bootstrap";

import * as CONSTANTS from "Constants";

import "assets/Runs.css";

const Runs = (viewRuns, runData, setRun) => {
  // Update when the runData changes
  useEffect(() => {
    console.log("Run Data Changed");
    console.log(runData);
  }, [runData]);

  if (viewRuns.viewRuns.length > 0) {
    return (
      <div className="sub-section run-card-holder">
        {viewRuns.viewRuns.map(function (run, i) {
          return (
            <Card className="run-card" key={i}>
              <Card.Body className="run-card-body">
                <Card.Title className="run-card-title">{run.value}</Card.Title>
                {runData[run.value] &&
                  runData[run.value]["card_info"]["n_faults"]}
                {runData[run.value] && (
                  <Card.Text className="run-card-text">
                    Number of Faults:{" "}
                    {runData[run.value]["card_info"]["n_faults"]}
                    Region: {runData[run.value]["card_info"]["region"]}
                    Grid Spacing: {runData[run.value]["card_info"]["grid"]}
                    Scientific Version:{" "}
                    {runData[run.value]["card_info"]["scientific_version"]}
                    Tectonic Types:{" "}
                    {runData[run.value]["card_info"]["tectonic_types"]}
                  </Card.Text>
                )}
                {!runData[run.value] && (
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
                )}
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
              </Card.Body>
            </Card>
          );
        })}
      </div>
    );
  }
};

export default memo(Runs);
