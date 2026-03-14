/**
 * Web-Inter-Prep Main JavaScript File
 * Refactored modular entrypoint
 */

import { api } from './services/api.js';
import {
    showMessage,
    showSpinner,
    hideSpinner,
    addFadeInAnimation,
    initializeScrollReveal,
    copyToClipboard,
} from './utils/dom.js';
import { displayQuestion, toggleHint, toggleAnswer } from './components/Question.js';
import { startTimer, stopTimer, endMockInterview } from './components/Timer.js';

// Global Variables
export let currentQuestion = null;

document.addEventListener('DOMContentLoaded', function () {
    initializeApp();
    initializeMoreDropdown();
    initializeScrollReveal();
});

function initializeApp() {
    addFadeInAnimation();

    setTimeout(function () {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function (alert) {
            if (alert.querySelector('.btn-close') && typeof bootstrap !== 'undefined') {
                const alertInstance =
                    bootstrap.Alert.getInstance(alert) || new bootstrap.Alert(alert);
                alertInstance.close();
            }
        });
    }, 5000);
}

function initializeMoreDropdown() {
    const moreDropdown = document.getElementById('moreDropdown');
    const moreMenu = document.querySelector('.more-dropdown');

    if (moreDropdown && moreMenu) {
        moreDropdown.addEventListener('show.bs.dropdown', function () {
            moreMenu.style.opacity = '0';
            moreMenu.style.transform = 'translateY(-10px)';

            setTimeout(() => {
                moreMenu.style.transition = 'all 0.3s ease-out';
                moreMenu.style.opacity = '1';
                moreMenu.style.transform = 'translateY(0)';
            }, 10);
        });

        moreDropdown.addEventListener('hide.bs.dropdown', function () {
            moreMenu.style.transition = 'all 0.2s ease-in';
            moreMenu.style.opacity = '0';
            moreMenu.style.transform = 'translateY(-10px)';
        });

        const menuItems = moreMenu.querySelectorAll('.dropdown-item');
        menuItems.forEach((item) => {
            item.addEventListener('mouseenter', function () {
                this.style.transform = 'translateX(8px)';
            });

            item.addEventListener('mouseleave', function () {
                this.style.transform = 'translateX(0)';
            });
        });

        menuItems.forEach((item) => {
            item.addEventListener('click', function (e) {
                const text = this.textContent.trim();
                switch (text) {
                    case 'Company Prep':
                    case 'AI Interview':
                    case 'Resume':
                    case 'Calendar':
                        e.preventDefault();
                        showMessage(`${text} feature coming soon!`, 'info');
                        break;
                    case 'DSA':
                    case 'Resources':
                    case 'Career Roadmap':
                        showMessage(`Opening ${text}...`, 'info');
                        break;
                }
            });
        });
    }
}

async function submitAnswer(questionId, isCorrect, userAnswer = '') {
    try {
        const data = await api.submitAnswer(questionId, isCorrect, userAnswer);
        if (data.success) {
            showMessage('Answer submitted successfully!', 'success');
            updateDashboardStats();
        } else {
            showMessage('Failed to submit answer. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('An error occurred. Please try again.', 'error');
    }
}

async function updateDashboardStats() {
    try {
        const data = await api.getStats();
        const elements = {
            'total-attempted': data.total_attempted,
            'correct-answers': data.correct_answers,
            accuracy: data.accuracy + '%',
            'weak-topics': data.weak_topics.length,
        };

        Object.keys(elements).forEach((id) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = elements[id];
            }
        });
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

async function loadNextQuestion() {
    showSpinner();
    try {
        const data = await api.getNextQuestion();
        hideSpinner();

        if (data.question) {
            currentQuestion = data.question;
            displayQuestion(data.question);
        } else {
            showMessage('No more questions available.', 'info');
        }
    } catch (error) {
        hideSpinner();
        console.error('Error:', error);
        showMessage('Failed to load question. Please try again.', 'error');
    }
}

async function loadMockQuestion() {
    showSpinner();
    try {
        const data = await api.getMockQuestion();
        hideSpinner();
        if (data.question) {
            currentQuestion = data.question;
            displayQuestion(data.question);
        } else if (data.error) {
            showMessage(data.error, 'error');
        } else {
            showMessage('No questions available.', 'info');
        }
    } catch (error) {
        hideSpinner();
        console.error('Error:', error);
        showMessage('Failed to load question. Please try again.', 'error');
    }
}

// Attach essentials to window object for global availability (useful for HTML inline handlers)
window.showMessage = window.showMessage || showMessage;
window.submitAnswer = window.submitAnswer || submitAnswer;
window.loadNextQuestion = window.loadNextQuestion || loadNextQuestion;
window.loadMockQuestion = window.loadMockQuestion || loadMockQuestion;
window.toggleHint = window.toggleHint || toggleHint;
window.toggleAnswer = window.toggleAnswer || toggleAnswer;
window.copyToClipboard = window.copyToClipboard || copyToClipboard;
window.startTimer = window.startTimer || startTimer;
window.stopTimer = window.stopTimer || stopTimer;
window.endMockInterview = window.endMockInterview || endMockInterview;
