const Utils = {
    // Format as Indian Rupee (₹1,23,456.00)
    formatCurrency: (amount) => {
        if (amount === null || amount === undefined) return '₹0.00';
        const num = parseFloat(amount);
        if (isNaN(num)) return '₹0.00';
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(num);
    },

    // Format as DD/MM/YYYY
    formatDate: (dateStr) => {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        if (isNaN(date.getTime())) return dateStr;
        return date.toLocaleDateString('en-GB');
    },

    // Format as DD/MM/YYYY HH:MM
    formatDateTime: (dateStr) => {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        if (isNaN(date.getTime())) return dateStr;
        return date.toLocaleDateString('en-GB') + ' ' + 
               date.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
    },

    // Debounce function
    debounce: (fn, delay) => {
        let timeoutId;
        return function(...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => fn.apply(this, args), delay);
        };
    },

    // Prevent XSS
    escapeHtml: (str) => {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    },

    // Safe decimal parsing
    parseDecimal: (value) => {
        if (typeof value === 'number') return value;
        if (!value) return 0.0;
        const parsed = parseFloat(value.toString().replace(/,/g, ''));
        return isNaN(parsed) ? 0.0 : parsed;
    },

    // Basic email validation
    validateEmail: (email) => {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(String(email).toLowerCase());
    },

    // Indian mobile validation (10 digits)
    validateMobile: (mobile) => {
        const re = /^[6-9]\d{9}$/;
        return re.test(String(mobile));
    },

    // Basic GSTIN format validation (15 chars)
    validateGSTIN: (gstin) => {
        const re = /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/;
        return re.test(String(gstin).toUpperCase());
    },

    // PAN format validation
    validatePAN: (pan) => {
        const re = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;
        return re.test(String(pan).toUpperCase());
    },

    // Truncate text
    truncateText: (text, maxLength) => {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    },

    showLoading: (element) => {
        if (element) {
            element.setAttribute('disabled', 'true');
            element.classList.add('loading');
        }
    },

    hideLoading: (element) => {
        if (element) {
            element.removeAttribute('disabled');
            element.classList.remove('loading');
        }
    }
};
