export function showMessage(message, type = 'info') {
    const alertClass = type === 'error' ? 'danger' : type;
    const alertHtml = `
        <div class="alert alert-${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    let messageContainer = document.getElementById('message-container');
    if (!messageContainer) {
        messageContainer = document.createElement('div');
        messageContainer.id = 'message-container';
        messageContainer.className = 'container mt-3';

        const nav = document.querySelector('nav');
        if (nav && nav.parentNode) {
            nav.parentNode.insertBefore(messageContainer, nav.nextSibling);
        } else {
            document.body.insertBefore(messageContainer, document.body.firstChild);
        }
    }

    messageContainer.innerHTML = alertHtml;

    setTimeout(function () {
        const alert = messageContainer.querySelector('.alert');
        if (alert && typeof bootstrap !== 'undefined') {
            const alertInstance = bootstrap.Alert.getInstance(alert) || new bootstrap.Alert(alert);
            alertInstance.close();
        }
    }, 5000);
}

export function showSpinner() {
    const spinner = document.createElement('div');
    spinner.className = 'spinner';
    spinner.id = 'loading-spinner';

    const container = document.querySelector('.container');
    if (container) {
        container.appendChild(spinner);
    }
}

export function hideSpinner() {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        spinner.remove();
    }
}

export function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(
        function () {
            showMessage('Copied to clipboard!', 'success');
        },
        function (err) {
            console.error('Could not copy text: ', err);
            showMessage('Failed to copy to clipboard', 'error');
        }
    );
}

export function addFadeInAnimation() {
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in');
        }, index * 100);
    });
}

export function initializeScrollReveal() {
    if (!window.IntersectionObserver) return;

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('reveal-in');
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.08, rootMargin: '0px 0px -40px 0px' }
    );

    const revealables = document.querySelectorAll(
        '.reveal-on-scroll, .card, .btn, .list-group-item'
    );
    revealables.forEach((el) => {
        el.classList.add('reveal-on-scroll');
        observer.observe(el);
    });
}
