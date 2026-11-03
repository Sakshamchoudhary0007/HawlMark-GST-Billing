let currentPage = 1;
const limit = 20;

function safeEscape(str) {
    if (typeof Utils !== 'undefined' && Utils.escapeHtml) {
        return Utils.escapeHtml(str);
    }
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function initCustomerList() {
    loadCustomers();
    
    document.getElementById('searchInput')?.addEventListener('input', (typeof Utils !== 'undefined' && Utils.debounce ? Utils.debounce : (fn, d) => fn)(() => {
        currentPage = 1;
        loadCustomers();
    }, 500));
    
    document.getElementById('includeArchivedCheckbox')?.addEventListener('change', () => {
        currentPage = 1;
        loadCustomers();
    });
}

async function loadCustomers() {
    const searchInput = document.getElementById('searchInput')?.value || '';
    const includeArchived = document.getElementById('includeArchivedCheckbox')?.checked || false;
    
    let url = `/api/customers?page=${currentPage}&limit=${limit}`;
    if (searchInput) {
        url += `&q=${encodeURIComponent(searchInput)}`;
    }
    if (includeArchived) {
        url += `&include_archived=true`;
    }
    
    try {
        const response = await API.get(url);
        renderCustomersTable(response.items || []);
        renderPagination(response.total || 0, response.page || 1, response.limit || limit, response.pages || 1);
    } catch (error) {
        if (typeof Toast !== 'undefined') Toast.error('Failed to load customers');
        console.error('Customer loading error:', error);
    }
}

function renderCustomersTable(customers) {
    const tbody = document.getElementById('customersTableBody');
    if (!tbody) return;
    
    if (customers.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 2rem; color: #64748b;">No customers found.</td></tr>`;
        return;
    }
    
    tbody.innerHTML = customers.map(customer => {
        const rowStyle = customer.is_archived ? 'opacity: 0.6;' : '';
        const statusBadge = customer.is_archived 
            ? `<span style="padding: 2px 6px; background: #e2e8f0; border-radius: 4px; font-size: 0.8rem;">Archived</span>`
            : `<span style="padding: 2px 6px; background: #dcfce7; color: #166534; border-radius: 4px; font-size: 0.8rem;">Active</span>`;
            
        return `
            <tr style="${rowStyle}">
                <td><strong>${safeEscape(customer.customer_name)}</strong></td>
                <td><span class="badge badge-outline" style="font-family:monospace; background:#eef2ff; color:#3730a3; padding:3px 8px; border-radius:4px; font-size:0.85rem;">${safeEscape(customer.licence_number || '-')}</span></td>
                <td>${safeEscape(customer.gstin || '-')}</td>
                <td>${safeEscape(customer.mobile || '-')}</td>
                <td>${safeEscape(customer.city || '')}${customer.state ? ', ' + safeEscape(customer.state) : ''}</td>
                <td>${statusBadge}</td>
                <td style="text-align: right; white-space: nowrap;">
                    <div style="display: inline-flex; gap: 0.35rem; align-items: center; justify-content: flex-end;">
                        <a href="/invoices/new?customer_id=${customer.id}" class="btn btn-primary" style="padding: 0.25rem 0.5rem; font-size: 0.82rem; white-space: nowrap;" title="Create invoice for this customer">➕ Invoice</a>
                        <a href="/customers/${customer.id}/edit" class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.82rem; white-space: nowrap;">Edit</a>
                        <button onclick="toggleArchiveCustomer(${customer.id}, ${!customer.is_archived})" class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.82rem; white-space: nowrap;">
                            ${customer.is_archived ? 'Unarchive' : 'Archive'}
                        </button>
                        <button onclick="deleteCustomer(${customer.id}, '${safeEscape(customer.customer_name)}')" class="btn btn-danger" style="padding: 0.25rem 0.5rem; font-size: 0.82rem; background: #ef4444; color: #ffffff; border: none; white-space: nowrap;">
                            Delete
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

function renderPagination(total, page, limit, pages) {
    const info = document.getElementById('paginationInfo');
    const controls = document.getElementById('paginationControls');
    if (!info || !controls) return;
    
    const start = total > 0 ? (page - 1) * limit + 1 : 0;
    const end = Math.min(page * limit, total);
    
    info.textContent = total > 0 ? `Showing ${start} to ${end} of ${total} entries` : 'No entries';
    
    let buttonsHtml = '';
    if (page > 1) {
        buttonsHtml += `<button onclick="changePage(${page - 1})" class="btn btn-secondary" style="padding: 0.25rem 0.5rem;">Prev</button>`;
    }
    
    if (page < pages) {
        buttonsHtml += `<button onclick="changePage(${page + 1})" class="btn btn-secondary" style="padding: 0.25rem 0.5rem;">Next</button>`;
    }
    
    controls.innerHTML = buttonsHtml;
}

function changePage(newPage) {
    currentPage = newPage;
    loadCustomers();
}

async function toggleArchiveCustomer(id, archive) {
    if (!confirm(`Are you sure you want to ${archive ? 'archive' : 'unarchive'} this customer?`)) return;
    
    try {
        await API.patch(`/api/customers/${id}/archive?archive=${archive}`);
        if (typeof Toast !== 'undefined') Toast.success(`Customer successfully ${archive ? 'archived' : 'unarchived'}`);
        loadCustomers();
    } catch (error) {
        if (typeof Toast !== 'undefined') Toast.error(error.message || 'Action failed');
    }
}

async function deleteCustomer(id, name) {
    if (!confirm(`Are you sure you want to permanently delete customer "${name}"?`)) return;
    
    try {
        await API.delete(`/api/customers/${id}`);
        if (typeof Toast !== 'undefined') Toast.success('Customer deleted successfully');
        loadCustomers();
    } catch (error) {
        if (typeof Toast !== 'undefined') Toast.error(error.message || 'Failed to delete customer');
    }
}

async function initCustomerForm() {
    const customerIdEl = document.getElementById('customerId');
    const customerId = customerIdEl ? customerIdEl.value : null;
    const form = document.getElementById('customerForm');
    
    if (customerId) {
        try {
            const customer = await API.get(`/api/customers/${customerId}`);
            populateForm(customer);
        } catch (error) {
            if (typeof Toast !== 'undefined') Toast.error('Failed to load customer details');
        }
    }
    
    // Auto-fetch GST on entering 15-digit GSTIN
    const gstinInput = document.getElementById('gstin');
    if (gstinInput) {
        let lastFetchedGstin = '';
        gstinInput.addEventListener('input', () => {
            const val = gstinInput.value.trim().toUpperCase();
            gstinInput.value = val;
            if (val.length === 15 && val !== lastFetchedGstin) {
                lastFetchedGstin = val;
                fetchGstDetails(val);
            }
        });
    }

    document.getElementById('verifyGstBtn')?.addEventListener('click', () => {
        const gstin = document.getElementById('gstin')?.value.trim();
        if (!gstin) {
            if (typeof Toast !== 'undefined') Toast.error('Please enter a 15-digit GSTIN first');
            return;
        }
        fetchGstDetails(gstin);
    });

    form?.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const saveBtn = document.getElementById('saveBtn');
        if (saveBtn) {
            saveBtn.disabled = true;
            saveBtn.textContent = 'Saving...';
        }
        
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        // Auto-extract PAN from GSTIN if present and PAN field is empty
        if (data.gstin && data.gstin.length === 15) {
            data.pan_number = data.gstin.substring(2, 12);
        }
        
        // Clean empty strings to null
        for (const key in data) {
            if (data[key] === '') {
                data[key] = null;
            }
        }
        
        try {
            if (customerId) {
                await API.put(`/api/customers/${customerId}`, data);
                if (typeof Toast !== 'undefined') Toast.success('Customer updated successfully');
            } else {
                await API.post('/api/customers', data);
                if (typeof Toast !== 'undefined') Toast.success('Customer created successfully');
            }
            window.location.href = '/customers';
            return;
        } catch (error) {
            if (typeof Toast !== 'undefined') Toast.error(error.message || 'Failed to save customer');
        } finally {
            if (saveBtn) {
                saveBtn.disabled = false;
                saveBtn.textContent = '💾 Save Customer';
            }
        }
    });
}

async function fetchGstDetails(gstin) {
    const verifyBtn = document.getElementById('verifyGstBtn');
    const oldText = verifyBtn ? verifyBtn.textContent : '';
    if (verifyBtn) {
        verifyBtn.textContent = 'Fetching...';
        verifyBtn.disabled = true;
    }
    
    const resultCard = document.getElementById('gstResultCard');
    
    try {
        const data = await API.get(`/api/gst/lookup?gstin=${encodeURIComponent(gstin)}`);
        
        // Auto-fill form fields
        if (data.legal_name) document.getElementById('customerName').value = data.legal_name;
        if (data.taxpayer_type) document.getElementById('taxpayerType').value = data.taxpayer_type;
        if (data.address_line1) document.getElementById('addressLine1').value = data.address_line1;
        if (data.address_line2) document.getElementById('addressLine2').value = data.address_line2;
        if (data.city) document.getElementById('city').value = data.city;
        if (data.state) document.getElementById('state').value = data.state;
        if (data.pincode) document.getElementById('pincode').value = data.pincode;
        if (data.state && document.getElementById('placeOfSupply')) {
            document.getElementById('placeOfSupply').value = data.state;
        }
        
        // Extract 10-digit PAN from GSTIN
        if (gstin.length === 15 && document.getElementById('panNumber')) {
            document.getElementById('panNumber').value = gstin.substring(2, 12);
        }
        
        // Show result card
        if (resultCard) {
            resultCard.style.display = 'block';
            resultCard.style.borderColor = '#10b981';
            resultCard.style.backgroundColor = '#f0fdf4';
            resultCard.innerHTML = `
                <div style="color: #166534; font-weight: bold; margin-bottom: 4px;">✓ GST Details & Address Auto-Fetched</div>
                <div style="font-size: 0.88rem; color: #1e293b; line-height: 1.4;">
                    <strong>Legal Name:</strong> ${safeEscape(data.legal_name)}<br>
                    <strong>State:</strong> ${safeEscape(data.state)}<br>
                    <strong>Address:</strong> ${safeEscape(data.address_line1 || '')} ${safeEscape(data.city || '')} ${safeEscape(data.pincode || '')}
                </div>
            `;
        }
        if (typeof Toast !== 'undefined') Toast.success('GST details and address auto-fetched successfully!');
    } catch (error) {
        if (resultCard) {
            resultCard.style.display = 'block';
            resultCard.style.borderColor = '#ef4444';
            resultCard.style.backgroundColor = '#fef2f2';
            resultCard.innerHTML = `
                <div style="color: #991b1b; font-weight: bold;">✗ GST Lookup Warning</div>
                <div style="font-size: 0.88rem; margin-top: 4px; color: #991b1b;">${safeEscape(error.message || 'Could not auto-fetch GST details. You can enter address manually.')}</div>
            `;
        }
    } finally {
        if (verifyBtn) {
            verifyBtn.textContent = oldText || '🔍 Fetch GST';
            verifyBtn.disabled = false;
        }
    }
}

function populateForm(data) {
    for (const key in data) {
        const inputId = key.replace(/_([a-z])/g, g => g[1].toUpperCase());
        const input = document.getElementById(inputId);
        if (input && data[key] !== null) {
            input.value = data[key];
        }
    }
}
