import React from 'react';
import './PageStyles.css';

function QuizPage() {
  const quizzes = JSON.parse(localStorage.getItem('quizzes') || '[]');

  return (
    <div className="text-wrapper">
      <div className="text-header">
        <p className="sub-title">Hi student,</p>
        <h2 className="main-title">🧠 퀴즈</h2>
      </div>

      <div className="quiz-box">
        <ul className="quiz-list">
          {quizzes.map((quiz, index) => (
            <li key={index} className="quiz-item">
              <strong className="quiz-type">[{quiz.type}]</strong> {quiz.question}
              <div className="quiz-answer">정답: <em>{quiz.answer}</em></div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default QuizPage;
