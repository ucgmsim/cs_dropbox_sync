import React, {useEffect, useState, memo } from "react";
import { Card, Placeholder } from "react-bootstrap";

import { RunCard } from "components";

import "assets/Runs.css";

const Runs = ({ viewRuns, runData, setRun }) => {

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
    </Placeholder>
  );

  const [selectedRun, setSelectedRun] = useState([]);

  const handleClick = (runName) => {
    // Sets the select run in the Form component
    setRun([runName]);
    setSelectedRun(runName);
  }

  if (Object.keys(runData).length > 0) {
    return (
      <div className="sub-section run-card-holder">
        {viewRuns.map(function (run, i) {
          return (
            <RunCard
              key={i}
              runData={runData[run.value]}
              setRun={handleClick}
              runName={run.value}
              active={selectedRun[0] === run.value}
            />
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
