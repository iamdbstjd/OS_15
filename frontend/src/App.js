import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import UploadPage from './pages/UploadPage';
import TextPage from './pages/TextPage';
import SummaryPage from './pages/SummaryPage';
import QuizPage from './pages/QuizPage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app-container">
        <Sidebar />
        <div className="main-content">
          <Routes>
            <Route path="/" element={<Navigate to="/upload" />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/text" element={<TextPage />} />
            <Route path="/summary" element={<SummaryPage />} />
            <Route path="/quiz" element={<QuizPage />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;