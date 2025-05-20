import React, { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './PageStyles.css';

function UploadPage() {
  const fileInputRef = useRef(null);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [isTranscribed, setIsTranscribed] = useState(false);
  const navigate = useNavigate();

  const handleButtonClick = () => {
    if (isTranscribed) {
      navigate('/text');
    } else {
      fileInputRef.current.click();
    }
  };

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (file) {
      const formData = new FormData();
      formData.append('audio_file', file);

      setLoading(true);
      setErrorMessage('');

      try {
        const response = await fetch('http://127.0.0.1:8000/process-lecture/', {
          method: 'POST',
          body: formData,
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || '서버 오류');
        }

        // Store result
        localStorage.setItem('transcript', data.transcription);
        localStorage.setItem('summary', data.summary);
        localStorage.setItem('quizzes', JSON.stringify(data.quizzes));

        // Show the "변환된 텍스트" button
        setIsTranscribed(true);
      } catch (error) {
        setErrorMessage(error.message || '알 수 없는 오류가 발생했습니다.');
      } finally {
        setLoading(false);
      }
    }
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
          {isTranscribed ? '📄변환된 텍스트' : '⬆ 음성파일 업로드'}
        </button>

        {!isTranscribed && (
          <input
            type="file"
            accept="audio/*"
            ref={fileInputRef}
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
        )}

        {loading && <p className="status">⏳ 변환 중...</p>}
        {errorMessage && <p className="error">❌ {errorMessage}</p>}
      </div>
    </div>
  );
}

export default UploadPage;
