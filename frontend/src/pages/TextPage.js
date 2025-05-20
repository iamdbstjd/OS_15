import React from 'react';
import './PageStyles.css';

function TextPage() {
  const transcript = localStorage.getItem('transcript') || '';

  return (
    <div className="text-wrapper">
      <div className="text-header">
        <p className="sub-title">Hi student,</p>
        <h2 className="main-title">📄 변환된 텍스트</h2>
      </div>

      <div className="text-box">
        <p className="text-content">{transcript}</p>
      </div>
    </div>
  );
}

export default TextPage;
