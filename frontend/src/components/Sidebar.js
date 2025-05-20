import React from 'react';
import { NavLink } from 'react-router-dom';
import './Sidebar.css';

function Sidebar() {
  return (
    <div className="sidebar">
      <h2 className="logo">🎧 StudyWithMe</h2>
      <nav>
        <NavLink to="/upload" className="nav-link">음성파일 업로드</NavLink>
        <NavLink to="/text" className="nav-link">텍스트 파일</NavLink>
        <NavLink to="/summary" className="nav-link">텍스트 요약</NavLink>
        <NavLink to="/quiz" className="nav-link">퀴즈</NavLink>
      </nav>
    </div>
  );
}

export default Sidebar;
