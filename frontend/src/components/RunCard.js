import React, { useEffect, useState, memo } from "react";
import { Card, Placeholder } from "react-bootstrap";

import * as CONSTANTS from "Constants";

import "assets/RunCard.css";

const RunCard = ({ runData, setRun, runName, loadingPlaceholder, active }) => {

  const handleClick = () => {
    // Sets the select run in the Form component
    setRun([runName]);
  };


  return (
    <Card className={'run-card ' +  (active ? "run-card-active" : "run-card")} onClick={handleClick}>
      <Card.Body className="run-card-body">
        {runData && (<Card.Title className="run-card-title">{runData["card_info"]["run_type"]}</Card.Title>)}
        {!runData && (<Card.Title className="run-card-title"><Placeholder as={Card.Title} animation="glow" xs={12}></Placeholder></Card.Title>)}
        <Card.Title className="run-card-sub-title">{runName}</Card.Title>
        {runData && (
          <Card.Text className="run-card-info-text">
            <b>Number of Faults:</b>{" "}
            {runData["card_info"]["n_faults"]}
            <br />
            <b>Region:</b> {runData["card_info"]["region"]}
            <br />
            <b>Grid Spacing:</b>{" "}
            {runData["card_info"]["grid_spacing"]}
            <br />
            <b>Tectonic Types:</b>{" "}
            {runData["card_info"]["tectonic_types"].join(", ")}
          </Card.Text>
        )}
        {!runData && loadingPlaceholder}
      </Card.Body>
    </Card>
  );
};

export default memo(RunCard);
