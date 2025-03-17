import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import FaceRegister from "./components/FaceRegister";
import FaceVerify from "./components/FaceVerify";

function App() {
    return (
      <Router>
      <Routes>
          <Route path="/" element={<FaceRegister />} />
          <Route path="/verify" element={<FaceVerify />} />
      </Routes>
  </Router>
    );
}

export default App;
