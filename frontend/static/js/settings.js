const SettingsManager = (function() {

    function initTabs() {
        const tabBusBtn = document.getElementById('tabBusinessBtn');
        const tabUsersBtn = document.getElementById('tabUsersBtn');
        const contentBus = document.getElementById('tabBusinessContent');
        const contentUsers = document.getElementById('tabUsersContent');
        const saveHeaderBtn = document.getElementById('saveBusinessHeaderBtn');

        if (tabBusBtn && tabUsersBtn) {
            tabBusBtn.addEventListener('click', () => {
                tabBusBtn.classList.add('active');
                tabBusBtn.style.color = '#2563eb';
                tabBusBtn.style.borderBottom = '3px solid #2563eb';
                
                tabUsersBtn.classList.remove('active');
                tabUsersBtn.style.color = '#64748b';
                tabUsersBtn.style.borderBottom = '3px solid transparent';

                contentBus.style.display = 'block';
                contentUsers.style.display = 'none';
                if (saveHeaderBtn) saveHeaderBtn.style.display = 'inline-block';
            });

            tabUsersBtn.addEventListener('click', () => {
                tabUsersBtn.classList.add('active');
                tabUsersBtn.style.color = '#2563eb';
                tabUsersBtn.style.borderBottom = '3px solid #2563eb';

                tabBusBtn.classList.remove('active');
                tabBusBtn.style.color = '#64748b';
                tabBusBtn.style.borderBottom = '3px solid transparent';

                contentBus.style.display = 'none';
                contentUsers.style.display = 'block';
                if (saveHeaderBtn) saveHeaderBtn.style.display = 'none';

                if (typeof loadUsers === 'function') loadUsers();
            });
        }
    }

    async function loadBusinessDetails() {
        try {
            const bus = await API.get('/api/business');
            if (!bus) return;

            const setValue = (id, val) => {
                const el = document.getElementById(id);
                if (el) el.value = val || '';
            };

            setValue('legalName', bus.legal_name);
            setValue('tradeName', bus.trade_name);
            setValue('busGstin', bus.gstin);
            setValue('busLicence', bus.licence_number);
            setValue('busPhone', bus.phone);
            setValue('busEmail', bus.email);
            setValue('busAddress1', bus.address_line1);
            setValue('busAddress2', bus.address_line2);
            setValue('busCity', bus.city);
            setValue('busPincode', bus.pincode);
            setValue('busState', bus.state);

            // Bank details
            setValue('bankName', bus.bank_name);
            setValue('bankAccountNumber', bus.bank_account_number);
            setValue('bankIfsc', bus.bank_ifsc);

        } catch (error) {
            console.error('Failed to load business details:', error);
        }
    }

    async function saveBusinessDetails(e) {
        if (e) e.preventDefault();

        const form = document.getElementById('businessForm');
        if (form && !form.reportValidity()) return;

        const payload = {
            legal_name: document.getElementById('legalName')?.value,
            trade_name: document.getElementById('tradeName')?.value || null,
            gstin: document.getElementById('busGstin')?.value || null,
            licence_number: document.getElementById('busLicence')?.value || null,
            phone: document.getElementById('busPhone')?.value || null,
            email: document.getElementById('busEmail')?.value || null,
            address_line1: document.getElementById('busAddress1')?.value || null,
            address_line2: document.getElementById('busAddress2')?.value || null,
            city: document.getElementById('busCity')?.value || null,
            pincode: document.getElementById('busPincode')?.value || null,
            state: document.getElementById('busState')?.value || null,
            bank_name: document.getElementById('bankName')?.value || null,
            bank_account_number: document.getElementById('bankAccountNumber')?.value || null,
            bank_ifsc: document.getElementById('bankIfsc')?.value || null
        };

        try {
            await API.put('/api/business', payload);
            if (typeof UI !== 'undefined' && UI.showToast) {
                UI.showToast('Business profile & Bank Details saved successfully', 'success');
            } else if (typeof Toast !== 'undefined') {
                Toast.success('Business profile & Bank Details saved successfully');
            } else {
                alert('Saved successfully!');
            }
        } catch (error) {
            const msg = error.message || 'Failed to save business settings';
            if (typeof UI !== 'undefined' && UI.showToast) {
                UI.showToast(msg, 'error');
            } else if (typeof Toast !== 'undefined') {
                Toast.error(msg);
            } else {
                alert(msg);
            }
        }
    }

    function init() {
        initTabs();
        loadBusinessDetails();

        const form = document.getElementById('businessForm');
        if (form) {
            form.addEventListener('submit', saveBusinessDetails);
        }
    }

    return {
        init,
        loadBusinessDetails,
        saveBusinessDetails
    };
})();
