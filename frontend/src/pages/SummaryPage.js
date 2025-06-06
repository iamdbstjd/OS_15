import React from 'react';
import { useNavigate } from 'react-router-dom';
import './PageStyles.css';

function SummaryPage() {
  const summary = localStorage.getItem('summary') || '';
  const hasSummary = summary.trim() !== '';
  const navigate = useNavigate();

  const handleGoToUpload = () => {
    navigate('/upload');
  };

  return (
    <div className="text-wrapper">
      <div className="text-header">
        <p className="sub-title">Hi student,</p>
        <h2 className="main-title">📝 요약</h2>
      </div>

      <div className="text-box">
        {hasSummary ? (
          <p className="text-content">{summary}</p>
        ) : (
          <div className="text-content center-placeholder">
            <p className="upload-message">먼저 파일을 업로드해주세요!</p>
            <button className="upload-btn" onClick={handleGoToUpload}>
              업로드하러 가기
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default SummaryPage;
