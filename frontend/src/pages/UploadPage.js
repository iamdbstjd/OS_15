import React, { useRef, useReducer, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './PageStyles.css';

const initialState = {
  status: 'idle',
  errorMessage: '',
};

function reducer(state, action) {
  switch (action.type) {
    case 'START_UPLOAD':
      return { status: 'loading', errorMessage: '' };
    case 'UPLOAD_SUCCESS':
      return { status: 'done', errorMessage: '' };
    case 'UPLOAD_ERROR':
      return { status: 'error', errorMessage: action.payload };
    case 'RESET':
      return initialState;
    case 'RESTORE':
      return { ...state, ...action.payload };
    default:
      return state;
  }
}

function UploadPage() {
  const fileInputRef = useRef(null);
  const navigate = useNavigate();
  const [state, dispatch] = useReducer(reducer, initialState);
  const { status, errorMessage } = state;

  const isTranscribed = status === 'done';

  useEffect(() => {
    const savedStatus = localStorage.getItem('status');
    if (savedStatus === 'loading' || savedStatus === 'done') {
      dispatch({ type: 'RESTORE', payload: { status: savedStatus } });
    }
  }, []);

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('audio_file', file);

    dispatch({ type: 'START_UPLOAD' });
    localStorage.setItem('status', 'loading');

    try {
      const response = await fetch('http://127.0.0.1:8000/process-lecture/', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || '서버 오류');
      }

      localStorage.setItem('transcript', data.transcription);
      localStorage.setItem('summary', data.summary);
      localStorage.setItem('quizzes', JSON.stringify(data.quizzes));
      localStorage.setItem('status', 'done');

      dispatch({ type: 'UPLOAD_SUCCESS' });
    } catch (error) {
      dispatch({ type: 'UPLOAD_ERROR', payload: error.message });
      localStorage.setItem('status', 'error');
    }
  };

  const handleButtonClick = () => {
    if (status === 'done') {
      navigate('/text');
    } else {
      fileInputRef.current?.click();
    }
  };

  const handleReset = () => {
    dispatch({ type: 'RESET' });
    localStorage.removeItem('status');
    localStorage.removeItem('transcript');
    localStorage.removeItem('summary');
    localStorage.removeItem('quizzes');
  };

  return (
    <div className="upload-wrapper">
      <div className="upload-header">
        <p className="sub-title">Hi student.</p>
        <h2 className="main-title">텍스트로 변환할 음성 파일을 업로드하세요!</h2>
      </div>

      <div className="upload-box">
        <h2>시험 준비의 종결</h2>
        <p>음성 파일을 업로드하면<br />텍스트로 변환, 요약, 퀴즈까지!</p>

        <button className="upload-btn" onClick={handleButtonClick}>
          {status === 'done'
            ? '📄 변환된 텍스트 보기'
            : status === 'loading'
            ? '⏳ 변환 중...'
            : '⬆ 음성파일 업로드'}
        </button>

        <input
          type="file"
          accept="audio/*"
          ref={fileInputRef}
          onChange={handleFileChange}
          style={{ display: 'none' }}
          disabled={status !== 'idle'}
        />

        {status === 'done' && (
          <button className="reset-btn" onClick={handleReset} style={{ marginTop: '10px' }}>
            ⟳ 새로운 파일 업로드
          </button>
        )}

        {errorMessage && <p className="error">❌ {errorMessage}</p>}
      </div>
    </div>
  );
}

export default UploadPage;
