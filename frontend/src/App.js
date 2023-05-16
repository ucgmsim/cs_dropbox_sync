import React from "react";

import { Form, Map } from "components";

import "assets/App.css";
import "bootstrap/dist/css/bootstrap.min.css";

function App() {
  return (
    <div>
      <div className="title">Cybershake</div>
      <div className="App d-flex flex-column h-100">
        <div className="row two-column-row">
          <div className="col-7">
            {/* <div className="border section"> */}
              <Form/>
            {/* </div> */}
          </div>
          <div className="col-5">
            {/* <div className="border section"> */}
              <Map/>
            {/* </div> */}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
