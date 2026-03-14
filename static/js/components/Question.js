import { getDifficultyColor } from '../utils/helpers.js';

export function displayQuestion(question) {
    const questionContainer = document.getElementById('question-container');
    if (!questionContainer) return;

    const questionHtml = `
        <div class="card question-card">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <span class="badge bg-${question.type === 'technical' ? 'primary' : 'success'} fs-6">
                        ${question.type.charAt(0).toUpperCase() + question.type.slice(1)}
                    </span>
                    <span class="badge bg-${getDifficultyColor(question.difficulty)} fs-6">
                        ${question.difficulty.charAt(0).toUpperCase() + question.difficulty.slice(1)}
                    </span>
                </div>
                
                <h4 class="card-title">${question.question}</h4>
                
                <div class="mt-4">
                    <button class="btn btn-outline-warning me-2" id="hint-btn-${question.id}" 
                            onclick="window.toggleHint(${question.id})">
                        <i class="fas fa-lightbulb me-2"></i>Show Hint
                    </button>
                    <button class="btn btn-outline-success me-2" id="answer-btn-${question.id}" 
                            onclick="window.toggleAnswer(${question.id})">
                        <i class="fas fa-check-circle me-2"></i>Show Answer
                    </button>
                    <button class="btn btn-primary" onclick="window.loadNextQuestion()">
                        <i class="fas fa-forward me-2"></i>Next Question
                    </button>
                </div>
                
                <div id="hint-${question.id}" class="hint-section" style="display: none;">
                    <h6><i class="fas fa-lightbulb me-2"></i>Hint:</h6>
                    <p>${question.hints}</p>
                </div>
                
                <div id="answer-${question.id}" class="answer-section" style="display: none;">
                    <h6><i class="fas fa-check-circle me-2"></i>Answer:</h6>
                    <p>${question.answer}</p>
                </div>
            </div>
        </div>
    `;

    questionContainer.innerHTML = questionHtml;
}

export function toggleHint(questionId) {
    const hintElement = document.getElementById(`hint-${questionId}`);
    const hintButton = document.getElementById(`hint-btn-${questionId}`);

    if (hintElement.style.display === 'none' || hintElement.style.display === '') {
        hintElement.style.display = 'block';
        hintButton.innerHTML = '<i class="fas fa-eye-slash me-2"></i>Hide Hint';
        hintButton.className = 'btn btn-warning';
    } else {
        hintElement.style.display = 'none';
        hintButton.innerHTML = '<i class="fas fa-lightbulb me-2"></i>Show Hint';
        hintButton.className = 'btn btn-outline-warning';
    }
}

export function toggleAnswer(questionId) {
    const answerElement = document.getElementById(`answer-${questionId}`);
    const answerButton = document.getElementById(`answer-btn-${questionId}`);

    if (answerElement.style.display === 'none' || answerElement.style.display === '') {
        answerElement.style.display = 'block';
        answerButton.innerHTML = '<i class="fas fa-eye-slash me-2"></i>Hide Answer';
        answerButton.className = 'btn btn-success';
    } else {
        answerElement.style.display = 'none';
        answerButton.innerHTML = '<i class="fas fa-check-circle me-2"></i>Show Answer';
        answerButton.className = 'btn btn-outline-success';
    }
}
