import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './PageStyles.css';

function QuizPage() {
  const quizzes = JSON.parse(localStorage.getItem('quizzes') || '[]');
  const hasQuizzes = quizzes.length > 0;
  const navigate = useNavigate();

  const [userAnswers, setUserAnswers] = useState(() => {
    const saved = localStorage.getItem('userAnswers');
    return saved ? JSON.parse(saved) : Array(quizzes.length).fill('');
  });

  const [showResults, setShowResults] = useState(() => {
    const saved = localStorage.getItem('showResults');
    return saved ? JSON.parse(saved) : false;
  });

  useEffect(() => {
    localStorage.setItem('userAnswers', JSON.stringify(userAnswers));
  }, [userAnswers]);

  useEffect(() => {
    localStorage.setItem('showResults', JSON.stringify(showResults));
  }, [showResults]);

  const handleGoToUpload = () => {
    navigate('/upload');
  };

  const handleInputChange = (index, value) => {
    const newAnswers = [...userAnswers];
    newAnswers[index] = value;
    setUserAnswers(newAnswers);
  };

  const handleOXClick = (index, value) => {
    const newAnswers = [...userAnswers];
    newAnswers[index] = value;
    setUserAnswers(newAnswers);
  };

  const handleSubmit = () => {
    setShowResults(true);
  };

  const handleRetry = () => {
    const resetAnswers = Array(quizzes.length).fill('');
    setUserAnswers(resetAnswers);
    setShowResults(false);
    localStorage.removeItem('userAnswers');
    localStorage.removeItem('showResults');
  };

  const isCorrect = (quiz, index) => {
    const answer = quiz?.answer;
    const userAnswer = userAnswers[index];

    if (answer == null || userAnswer == null) return false;

    const correct = answer.toString().trim().toLowerCase();
    const user = userAnswer.toString().trim().toLowerCase();
    return correct === user;
  };

  const renderInput = (quiz, index) => {
    const correct = isCorrect(quiz, index);
    const mark = correct ? '✔️' : '❌';
    const showAnswer = showResults;

    if (quiz.type === '빈칸') {
      return (
        <div className={`blank-input-wrapper ${showResults ? (correct ? 'correct-box' : 'incorrect-box') : ''}`}>
          <div className="input-mark-wrapper">
            <input
              type="text"
              className="quiz-input"
              value={userAnswers[index]}
              onChange={(e) => handleInputChange(index, e.target.value)}
              disabled={showResults}
            />
            {showResults && <span className="mark">{mark}</span>}
          </div>
          {showAnswer && (
            <div className="answer-text">
              정답: <strong>{quiz.answer}</strong>
            </div>
          )}
        </div>
      );
    } else if (quiz.type === 'O/X') {
      return (
        <div className="ox-buttons-wrapper">
          <div className="ox-buttons">
            {['O', 'X'].map((val) => {
              const selected = userAnswers[index] === val;
              const correctAnswer = isCorrect(quiz, index);

              return (
                <button
                  key={val}
                  className={`ox-button ${selected ? (showResults ? (correctAnswer ? 'correct' : 'incorrect') : 'selected') : ''}`}
                  onClick={() => handleOXClick(index, val)}
                  disabled={showResults}
                >
                  {val}
                </button>
              );
            })}
          </div>
          {showAnswer && (
            <div className="answer-text">
              정답: <strong>{quiz.answer}</strong>
            </div>
          )}
        </div>
      );
    }

    return null;
  };

  const correctCount = quizzes.filter((quiz, index) => isCorrect(quiz, index)).length;

  return (
    <div className="text-wrapper">
      <div className="text-header">
        <p className="sub-title">Hi student,</p>
        <h2 className="main-title">🧠 퀴즈</h2>
      </div>

      <div className="quiz-box">
        {hasQuizzes ? (
          <ul className="quiz-list">
            {quizzes.map((quiz, index) => (
              <li key={index} className="quiz-item">
                <div className={`quiz-question ${showResults && isCorrect(quiz, index) ? 'highlight' : ''}`}>
                  <strong className="quiz-type">[{quiz.type}]</strong> {quiz.question}
                </div>
                {renderInput(quiz, index)}
              </li>
            ))}
          </ul>
        ) : (
          <div className="text-content center-placeholder">
            <p className="upload-message">먼저 파일을 업로드해주세요!</p>
            <button className="upload-btn" onClick={handleGoToUpload}>
              업로드하러 가기
            </button>
          </div>
        )}

        {hasQuizzes && !showResults && (
          <div style={{ textAlign: 'right' }}>
            <button className="upload-btn" onClick={handleSubmit}>채점하기 ➤</button>
          </div>
        )}

        {showResults && (
          <div className="score-box">
            <p>{quizzes.length}개 중 {correctCount}개 정답</p>
            <button className="upload-btn" onClick={handleRetry}>다시 풀기</button>
          </div>
        )}
      </div>
    </div>
  );
}

export default QuizPage;
