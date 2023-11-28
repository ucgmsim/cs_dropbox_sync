import React, {useState} from "react";

import {Form, InstallCard, Map, Interests, Download, AddRun} from "components";

import Stepper from '@mui/material/Stepper';
import Step from '@mui/material/Step';
import StepButton from '@mui/material/StepButton';

import "assets/App.css";
import "bootstrap/dist/css/bootstrap.min.css";
import {Button} from "react-bootstrap";

function App() {

  const [showDownloadPopup, setShowDownloadPopup] = useState(false);
  const [interests, setInterests] = useState([]);
  const [selectedRun, setSelectedRun] = useState([]);
  const [selectedRunData, setSelectedRunData] = useState([]);
  const [activeStep, setActiveStep] = React.useState(0);
  const [completed, setCompleted] = React.useState({});
  const [showAdd, setShowAdd] = useState(false);
  const [addRunButtonText, setAddRunButtonText] = useState("Add Run");

  const steps = ['Interests', 'Select Dataset', 'Download Data'];

  const onCloseDownloadPopup = () => {
    setShowDownloadPopup(false);
  };

  const handleShowDownloadPopup = () => {
    setShowDownloadPopup(true);
  };

  const setInterest = (sites, sources) => {
    setInterests([{"sites": sites}, {"sources": sources}]);
    setCompleted({0: true});
    setActiveStep(1);
  }

  const setDataset = (selectedRun, selectedRunData) => {
    setSelectedRun(selectedRun);
    setSelectedRunData(selectedRunData);
    if (selectedRun.length > 0) {
      setCompleted({0: true, 1: true});
      setActiveStep(2);
    }
  }

  const goBack = () => {
    setActiveStep(0);
    setCompleted({0: false, 1: false});
  }

  const goForm = () => {
    setActiveStep(1);
    setCompleted({0: true, 1: false, 2: false})
  }

  const setShowAddForm = () => {
    if (showAdd) {
      setAddRunButtonText("Add Run");
      setShowAdd(false);
    } else {
      setAddRunButtonText("Back");
      setShowAdd(true);
    }
  }

  return (
    <div>
      <div className="App d-flex flex-column h-100">
        <div className="row two-column-row">
          <div className="col-7 left-side-title">
            <div className="title">Simulation Data</div>
          </div>
          <div className="col-5 right-side-title">
            <Button
              variant="secondary"
              className="add-run-button"
              onClick={setShowAddForm}
            >
              {addRunButtonText}
            </Button>
          </div>
        </div>
        {showAdd && <AddRun/>}
        {!showAdd &&
          <div className="row two-column-row">
            <div className="col-7 h-100">
              <Stepper className={"stepper"} nonLinear activeStep={activeStep}>
                {steps.map((label, index) => (
                  <Step key={label} completed={completed[index]}>
                    <StepButton color="inherit" disabled={true}>
                      {label}
                    </StepButton>
                  </Step>
                ))}
              </Stepper>
              {activeStep === 0 && <Interests setInterest={setInterest}/>}
              {activeStep === 1 && <Form interests={interests} setDataset={setDataset} goBack={goBack}/>}
              {activeStep === 2 &&
                <Download openPopup={handleShowDownloadPopup} selectedRunData={selectedRunData}
                          selectedRun={selectedRun}
                          goBack={goForm}/>}
            </div>
            <div className="col-5 h-100">
              <Map/>
            </div>
          </div>
        }
        {showDownloadPopup && <div className="popup-overlay">
          <div className="popup-content">
            <InstallCard onClose={onCloseDownloadPopup}/>
          </div>
        </div>}
      </div>
    </div>
  );
}

export default App;
