import { showMessage } from '../utils/dom.js';

let timerInterval = null;
export let sessionStartTime = null;

export function startTimer(duration) {
    sessionStartTime = new Date();
    let timeRemaining = duration * 60;

    const timerElement = document.getElementById('timer-display');
    if (!timerElement) return;

    timerInterval = setInterval(function () {
        const minutes = Math.floor(timeRemaining / 60);
        const seconds = timeRemaining % 60;

        timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

        if (timeRemaining <= 300) {
            timerElement.className = 'timer-display text-danger';
        } else if (timeRemaining <= 600) {
            timerElement.className = 'timer-display text-warning';
        }

        if (timeRemaining <= 0) {
            clearInterval(timerInterval);
            endMockInterview();
        }

        timeRemaining--;
    }, 1000);
}

export function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

export function endMockInterview() {
    stopTimer();
    showMessage('Mock interview session completed!', 'info');
    setTimeout(function () {
        window.location.href = '/mock/results';
    }, 2000);
}
