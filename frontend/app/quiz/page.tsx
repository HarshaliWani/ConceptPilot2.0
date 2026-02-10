'use client';

import React, { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { getQuiz, submitQuiz, QuizData, QuizResult } from '../../src/services/api';
import QuizCard from '../../src/components/QuizCard';
import QuizResults from '../../src/components/QuizResults';
import { getUserId } from '../../src/lib/auth';

const QuizPage = () => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const quizId = searchParams.get('id');

  const [quiz, setQuiz] = useState<QuizData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Quiz state
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [timeLeft, setTimeLeft] = useState(1800); // 30 minutes in seconds
  const [quizSubmitted, setQuizSubmitted] = useState(false);
  const [quizResult, setQuizResult] = useState<QuizResult | null>(null);
  const [reviewMode, setReviewMode] = useState(false);

  // Load quiz data
  useEffect(() => {
    const loadQuiz = async () => {
      if (!quizId) {
        setError('No quiz ID provided');
        setLoading(false);
        return;
      }

      try {
        const data = await getQuiz(quizId);
        setQuiz(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to load quiz');
        setLoading(false);
        console.error(err);
      }
    };

    loadQuiz();
  }, [quizId]);

  // Timer countdown
  useEffect(() => {
    if (!quiz || quizSubmitted || reviewMode) return;

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          handleSubmitQuiz();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [quiz, quizSubmitted, reviewMode]);

  const handleAnswerSelect = (questionIndex: number, optionIndex: number) => {
    if (reviewMode) return;
    setAnswers((prev) => ({
      ...prev,
      [questionIndex]: optionIndex,
    }));
  };

  const handleSubmitQuiz = async () => {
    if (!quiz || !quizId) return;

    const timeTaken = 1800 - timeLeft;
    const userId = getUserId();
    const lessonId = searchParams.get('lessonId');

    // Map answers from question index → question ID
    const mappedAnswers: Record<string, number> = {};
    for (const [indexStr, optionIdx] of Object.entries(answers)) {
      const qIndex = Number(indexStr);
      const question = quiz.questions[qIndex];
      if (question) {
        mappedAnswers[question.id] = optionIdx;
      }
    }

    try {
      const result = await submitQuiz(quizId, {
        user_id: userId,
        quiz_id: quizId,
        lesson_id: lessonId || undefined,
        answers: mappedAnswers,
        time_taken_seconds: timeTaken
      });
      setQuizResult(result);
      setQuizSubmitted(true);
    } catch (err) {
      setError('Failed to submit quiz');
      console.error(err);
    }
  };

  const handleReviewAnswers = () => {
    setReviewMode(true);
    setQuizSubmitted(false);
    setCurrentQuestionIndex(0);
  };

  const handleReturnToDashboard = () => {
    router.push('/');
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  const getProgressPercentage = () => {
    if (!quiz) return 0;
    return ((currentQuestionIndex + 1) / quiz.questions.length) * 100;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-zinc-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-zinc-600">Loading quiz...</p>
        </div>
      </div>
    );
  }

  if (error || !quiz) {
    return (
      <div className="min-h-screen bg-zinc-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg border border-zinc-200 max-w-md text-center">
          <div className="text-zinc-500 text-5xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-zinc-900 mb-2">Error</h2>
          <p className="text-zinc-600 mb-6">{error || 'Quiz not found'}</p>
          <button
            onClick={handleReturnToDashboard}
            className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  // Show results screen
  if (quizSubmitted && quizResult) {
    return (
      <div className="min-h-screen bg-zinc-50 py-8 px-4">
        <QuizResults
          result={quizResult}
          onReviewAnswers={handleReviewAnswers}
          onReturnToDashboard={handleReturnToDashboard}
        />
      </div>
    );
  }

  const currentQuestion = quiz.questions[currentQuestionIndex];
  const isLastQuestion = currentQuestionIndex === quiz.questions.length - 1;
  const answeredCount = Object.keys(answers).length;

  return (
    <div className="min-h-screen bg-zinc-50">
      {/* Header */}
      <div className="bg-white border-b border-zinc-200 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h1 className="text-2xl font-bold text-zinc-900">{quiz.topic_description || quiz.topic}</h1>
              <p className="text-sm text-zinc-600">{quiz.topic}</p>
            </div>
            {!reviewMode && (
              <div className={`text-2xl font-bold ${timeLeft < 300 ? 'text-zinc-900' : 'text-zinc-700'}`}>
                ⏱️ {formatTime(timeLeft)}
              </div>
            )}
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-zinc-200 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${getProgressPercentage()}%` }}
            ></div>
          </div>

          {/* Question Counter */}
          <div className="flex justify-between items-center mt-2 text-sm">
            <span className="text-zinc-600">
              Question {currentQuestionIndex + 1} of {quiz.questions.length}
            </span>
            <span className="text-zinc-600">
              Answered: {answeredCount}/{quiz.questions.length}
            </span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <QuizCard
          question={currentQuestion}
          questionNumber={currentQuestionIndex + 1}
          selectedAnswer={answers[currentQuestionIndex] ?? null}
          onAnswerSelect={(optionIndex) => handleAnswerSelect(currentQuestionIndex, optionIndex)}
          showResults={reviewMode}
        />

        {/* Navigation */}
        <div className="mt-6 flex items-center justify-between gap-4">
          <button
            onClick={() => setCurrentQuestionIndex((prev) => Math.max(0, prev - 1))}
            disabled={currentQuestionIndex === 0}
            className="px-6 py-3 border-2 border-zinc-300 text-zinc-700 rounded-lg font-medium hover:bg-zinc-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            ← Previous
          </button>

          <div className="flex gap-2 flex-wrap justify-center">
            {quiz.questions.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentQuestionIndex(index)}
                className={`w-10 h-10 rounded-lg font-medium transition-colors ${
                  index === currentQuestionIndex
                    ? 'bg-blue-500 text-white'
                    : answers[index] !== undefined
                    ? 'bg-blue-100 text-blue-700 border-2 border-blue-300'
                    : 'bg-zinc-100 text-zinc-600 border-2 border-zinc-300'
                }`}
              >
                {index + 1}
              </button>
            ))}
          </div>

          {isLastQuestion && !reviewMode ? (
            <button
              onClick={handleSubmitQuiz}
              disabled={answeredCount !== quiz.questions.length}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Submit Quiz ✓
            </button>
          ) : reviewMode && isLastQuestion ? (
            <button
              onClick={handleReturnToDashboard}
              className="px-6 py-3 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 transition-colors"
            >
              Finish Review →
            </button>
          ) : (
            <button
              onClick={() => setCurrentQuestionIndex((prev) => Math.min(quiz.questions.length - 1, prev + 1))}
              disabled={currentQuestionIndex === quiz.questions.length - 1}
              className="px-6 py-3 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Next →
            </button>
          )}
        </div>

        {/* Warning if not all answered */}
        {!reviewMode && isLastQuestion && answeredCount !== quiz.questions.length && (
          <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-blue-900 text-center">
              ⚠️ Please answer all questions before submitting ({answeredCount}/{quiz.questions.length} answered)
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default QuizPage;
