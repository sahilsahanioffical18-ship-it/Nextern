export const api = {
    async submitAnswer(questionId, isCorrect, userAnswer = '') {
        const response = await fetch('/submit-answer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question_id: questionId,
                correct: isCorrect,
                user_answer: userAnswer,
            }),
        });
        return response.json();
    },

    async getStats() {
        const response = await fetch('/api/stats');
        return response.json();
    },

    async getNextQuestion() {
        const response = await fetch('/api/next-question');
        return response.json();
    },

    async getMockQuestion() {
        const response = await fetch('/mock/question');
        return response.json();
    },
};
