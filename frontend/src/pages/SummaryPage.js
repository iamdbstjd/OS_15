import React from 'react';
import './PageStyles.css';

function SummaryPage() {
  const summary = localStorage.getItem('summary') || '';

  return (
    <div className="text-wrapper">
      <div className="text-header">
        <p className="sub-title">Hi student,</p>
        <h2 className="main-title">📝 요약</h2>
      </div>

      <div className="text-box">
        <p className="text-content">{summary}</p>
      </div>
    </div>
  );
}

export default SummaryPage;
