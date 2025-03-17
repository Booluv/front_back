import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import FaceRegister from "./components/FaceRegister";
import FaceVerify from "./components/FaceVerify";
import Masking from "./components/masking"; // ✅ Masking 컴포넌트 추가

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<FaceRegister />} />
                <Route path="/verify" element={<FaceVerify />} />
                <Route path="/masking" element={<Masking />} />  {/* ✅ 마스킹 페이지 추가 */}
            </Routes>
        </Router>
    );
}

export default App;
