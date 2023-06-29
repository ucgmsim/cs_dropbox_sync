import React from "react";

import { Form, Map } from "components";

import "assets/App.css";
import "bootstrap/dist/css/bootstrap.min.css";

function App() {
  return (
    <div>
      <div className="title">Simulation Data</div>
      <div className="App d-flex flex-column h-100">
        <div className="row two-column-row">
          <div className="col-7 h-100">
            <Form />
          </div>
          <div className="col-5 h-100">
            <Map />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
