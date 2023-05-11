import React from "react";

import { Form } from "components";

import "assets/App.css";
import "bootstrap/dist/css/bootstrap.min.css";

function App() {
  return (
    <div>
      <div className="header">Simulation Data</div>
      <div className="App d-flex flex-column h-100">
        <Form/>
      </div>
    </div>
  );
}

export default App;
