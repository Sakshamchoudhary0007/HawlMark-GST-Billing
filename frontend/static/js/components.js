const Toast = {
    container: null,
    
    init() {
        this.container = document.getElementById('toast-container');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        }
    },
    
    show(message, type = 'info', duration = 3000) {
        if (!this.container) this.init();
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const text = document.createElement('span');
        text.textContent = message;
        toast.appendChild(text);
        
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '&times;';
        closeBtn.className = 'toast-close';
        closeBtn.onclick = () => {
            toast.classList.add('toast-hiding');
            setTimeout(() => toast.remove(), 300);
        };
        toast.appendChild(closeBtn);
        
        this.container.appendChild(toast);
        
        // Trigger reflow for animation
        toast.offsetHeight;
        toast.classList.add('toast-show');
        
        setTimeout(() => {
            if (toast.parentElement) {
                toast.classList.add('toast-hiding');
                toast.classList.remove('toast-show');
                setTimeout(() => toast.remove(), 300);
            }
        }, duration);
    },
    
    success(message) { this.show(message, 'success'); },
    error(message) { this.show(message, 'error', 5000); },
    warning(message) { this.show(message, 'warning'); },
    info(message) { this.show(message, 'info'); }
};

const Modal = {
    show(options) {
        const { title, content, onConfirm, onCancel, confirmText = 'Confirm', cancelText = 'Cancel' } = options;
        
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        
        const modal = document.createElement('div');
        modal.className = 'modal-content';
        
        const header = document.createElement('div');
        header.className = 'modal-header';
        header.innerHTML = `<h3>${Utils.escapeHtml(title)}</h3>`;
        
        const body = document.createElement('div');
        body.className = 'modal-body';
        body.innerHTML = content; // Allows HTML string
        
        const footer = document.createElement('div');
        footer.className = 'modal-footer';
        
        if (onCancel) {
            const cancelBtn = document.createElement('button');
            cancelBtn.className = 'btn btn-secondary';
            cancelBtn.textContent = cancelText;
            cancelBtn.onclick = () => {
                onCancel();
                this.hide(overlay);
            };
            footer.appendChild(cancelBtn);
        }
        
        if (onConfirm) {
            const confirmBtn = document.createElement('button');
            confirmBtn.className = 'btn btn-primary';
            confirmBtn.textContent = confirmText;
            confirmBtn.onclick = () => {
                onConfirm();
                this.hide(overlay);
            };
            footer.appendChild(confirmBtn);
        }
        
        modal.appendChild(header);
        modal.appendChild(body);
        modal.appendChild(footer);
        overlay.appendChild(modal);
        
        document.body.appendChild(overlay);
    },
    
    hide(overlayElement) {
        if (overlayElement && overlayElement.parentElement) {
            overlayElement.remove();
        } else {
            const overlays = document.querySelectorAll('.modal-overlay');
            overlays.forEach(el => el.remove());
        }
    },
    
    confirm(message, onConfirm) {
        this.show({
            title: 'Confirm Action',
            content: `<p>${Utils.escapeHtml(message)}</p>`,
            onConfirm: onConfirm,
            onCancel: () => {}
        });
    }
};

const Pagination = {
    render(container, { page, limit, total, onPageChange }) {
        if (!container) return;
        container.innerHTML = '';
        
        const totalPages = Math.ceil(total / limit);
        if (totalPages <= 1) return;
        
        const wrapper = document.createElement('div');
        wrapper.className = 'pagination';
        
        // Prev button
        const prev = document.createElement('button');
        prev.className = 'page-btn';
        prev.textContent = '«';
        prev.disabled = page === 1;
        prev.onclick = () => onPageChange(page - 1);
        wrapper.appendChild(prev);
        
        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            const btn = document.createElement('button');
            btn.className = `page-btn ${i === page ? 'active' : ''}`;
            btn.textContent = i;
            btn.onclick = () => onPageChange(i);
            wrapper.appendChild(btn);
        }
        
        // Next button
        const next = document.createElement('button');
        next.className = 'page-btn';
        next.textContent = '»';
        next.disabled = page === totalPages;
        next.onclick = () => onPageChange(page + 1);
        wrapper.appendChild(next);
        
        container.appendChild(wrapper);
    }
};

const Loading = {
    show(container) {
        if (!container) return;
        container.classList.add('position-relative');
        
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = '<div class="spinner"></div>';
        
        container.appendChild(overlay);
    },
    
    hide(container) {
        if (!container) return;
        const overlay = container.querySelector('.loading-overlay');
        if (overlay) overlay.remove();
        container.classList.remove('position-relative');
    },
    
    skeleton(container, rows = 5) {
        if (!container) return;
        let html = '';
        for (let i = 0; i < rows; i++) {
            html += '<div class="skeleton-row"></div>';
        }
        container.innerHTML = html;
    }
};

const EmptyState = {
    render(container, { icon = '📄', title, message, actionText, onAction }) {
        if (!container) return;
        
        const wrapper = document.createElement('div');
        wrapper.className = 'empty-state';
        
        wrapper.innerHTML = `
            <div class="empty-icon">${icon}</div>
            <h3 class="empty-title">${Utils.escapeHtml(title)}</h3>
            <p class="empty-message">${Utils.escapeHtml(message)}</p>
        `;
        
        if (actionText && onAction) {
            const btn = document.createElement('button');
            btn.className = 'btn btn-primary mt-3';
            btn.textContent = actionText;
            btn.onclick = onAction;
            wrapper.appendChild(btn);
        }
        
        container.innerHTML = '';
        container.appendChild(wrapper);
    }
};

function showToast(message, type = 'success') {
    Toast.show(message, type);
}

window.showToast = showToast;
window.UI = window.UI || {};
window.UI.showToast = showToast;

document.addEventListener('DOMContentLoaded', () => {
    Toast.init();
});
