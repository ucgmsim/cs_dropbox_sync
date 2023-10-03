import React, {useState} from "react";

import {Form, InstallCard, Map} from "components";

import "assets/App.css";
import "bootstrap/dist/css/bootstrap.min.css";

function App() {

  const [showDownloadPopup, setShowDownloadPopup] = useState(false);

  const onCloseDownloadPopup = () => {
    setShowDownloadPopup(false);
  };

  const handleShowDownloadPopup = () => {
    setShowDownloadPopup(true);
  };


  return (
    <div>
      <div className="title">Simulation Data</div>
      <div className="App d-flex flex-column h-100">
        <div className="row two-column-row">
          <div className="col-7 h-100">
            <Form openPopup={handleShowDownloadPopup}/>
          </div>
          <div className="col-5 h-100">
            <Map />
          </div>
        </div>
        {showDownloadPopup && <div className="popup-overlay">
          <div className="popup-content">
            <InstallCard onClose={onCloseDownloadPopup} />
          </div>
        </div>}
      </div>
    </div>
  );
}

export default App;
