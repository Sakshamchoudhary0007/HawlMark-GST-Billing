const InvoiceManager = (function() {
    let customersList = [];
    let productsList = [];
    let businessDetails = null;
    let editingInvoiceId = null;

    function getTodayLocalDateString() {
        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, '0');
        const dd = String(today.getDate()).padStart(2, '0');
        return `${yyyy}-${mm}-${dd}`;
    }

    // --- Create Invoice Logic ---
    async function initCreate(editInvoiceId = null) {
        editingInvoiceId = editInvoiceId;
        const invDate = document.getElementById('invoiceDate');
        if (invDate && !editingInvoiceId) invDate.value = getTodayLocalDateString();

        try {
            let custRes = { items: [] };
            let prodRes = { items: [] };
            let busRes = null;

            try { custRes = await API.get('/api/customers?limit=1000'); } catch(e) { console.warn('Customers fetch warning:', e); }
            try { prodRes = await API.get('/api/products?limit=1000'); } catch(e) { console.warn('Products fetch warning:', e); }
            try { busRes = await API.get('/api/business'); } catch(e) { console.warn('Business details fetch warning:', e); }
            
            customersList = custRes.items || [];
            productsList = prodRes.items || [];
            businessDetails = busRes;

            setupCustomerSelector();
            
            const DEFAULT_TERMS = `1. E. & O.E.
2. Received the precious metal / Jewellery in satisfactory Condition.
3. Subject to 'Palghar' Jurisdiction only.`;

            // Set default terms & footer from business settings if present
            const termsEl = document.getElementById('terms');
            if (termsEl && !editingInvoiceId) {
                if (businessDetails && businessDetails.invoice_terms) {
                    termsEl.value = businessDetails.invoice_terms;
                } else if (!termsEl.value.trim()) {
                    termsEl.value = DEFAULT_TERMS;
                }
            }
            if (businessDetails && businessDetails.invoice_footer && document.getElementById('notes') && !editingInvoiceId) {
                document.getElementById('notes').value = businessDetails.invoice_footer;
            }

            if (editingInvoiceId) {
                const invToEdit = await API.get('/api/invoices/' + editingInvoiceId);
                if (!invToEdit || invToEdit.status !== 'DRAFT') {
                    if (typeof Toast !== 'undefined') Toast.error('Only draft invoices can be edited');
                    window.location.href = `/invoices/${editingInvoiceId}`;
                    return;
                }

                if (invDate && invToEdit.invoice_date) invDate.value = invToEdit.invoice_date;
                if (invToEdit.tax_mode) document.getElementById('taxMode').value = invToEdit.tax_mode;
                if (document.getElementById('reverseCharge')) document.getElementById('reverseCharge').checked = !!invToEdit.reverse_charge;
                if (invToEdit.notes !== undefined && document.getElementById('notes')) document.getElementById('notes').value = invToEdit.notes || '';
                if (invToEdit.terms !== undefined && termsEl) termsEl.value = invToEdit.terms || '';

                if (invToEdit.customer_id) {
                    selectCustomerById(invToEdit.customer_id);
                }

                const firstItemGst = (invToEdit.items && invToEdit.items.length > 0) ? parseFloat(invToEdit.items[0].gst_rate) : 3.0;
                if (invToEdit.tax_mode === 'CGST_SGST') {
                    const halfGst = firstItemGst / 2;
                    if (document.getElementById('cgstPercent')) document.getElementById('cgstPercent').value = halfGst;
                    if (document.getElementById('sgstPercent')) document.getElementById('sgstPercent').value = halfGst;
                } else {
                    if (document.getElementById('igstPercent')) document.getElementById('igstPercent').value = firstItemGst;
                }

                const tbody = document.getElementById('lineItemsBody');
                if (tbody) tbody.innerHTML = '';
                if (invToEdit.items && invToEdit.items.length > 0) {
                    invToEdit.items.forEach(item => addLineItemWithData(item));
                } else {
                    addLineItem();
                }
                calculateSummary();
            } else {
                // Check URL query parameters for pre-selected customer_id
                const urlParams = new URLSearchParams(window.location.search);
                const preselectedCustId = urlParams.get('customer_id');
                if (preselectedCustId) {
                    let custExists = customersList.some(c => c.id == preselectedCustId);
                    if (!custExists) {
                        try {
                            const singleCust = await API.get('/api/customers/' + preselectedCustId);
                            if (singleCust && singleCust.id) {
                                customersList.push(singleCust);
                            }
                        } catch(err) {
                            console.warn('Pre-selected customer fetch warning:', err);
                        }
                    }
                    selectCustomerById(preselectedCustId);
                }

                // Add initial line item
                addLineItem();
            }

        } catch (e) {
            console.error('Invoice creation load error:', e);
            if (typeof Toast !== 'undefined') Toast.error('Error loading data for invoice');
        }

        document.getElementById('addLineItemBtn').addEventListener('click', addLineItem);
        document.getElementById('taxMode').addEventListener('change', calculateSummary);
        document.getElementById('reverseCharge').addEventListener('change', calculateSummary);
        document.getElementById('saveDraftBtn').addEventListener('click', saveDraft);

        const cgstInp = document.getElementById('cgstPercent');
        const sgstInp = document.getElementById('sgstPercent');
        const igstInp = document.getElementById('igstPercent');

        if (cgstInp) {
            cgstInp.addEventListener('input', () => {
                if (sgstInp) sgstInp.value = cgstInp.value;
                calculateSummary();
            });
        }
        if (sgstInp) sgstInp.addEventListener('input', calculateSummary);
        if (igstInp) igstInp.addEventListener('input', calculateSummary);
    }

    function setupCustomerSelector() {
        const searchInput = document.getElementById('customerSearchInput');
        const hiddenInput = document.getElementById('customerId');
        const dropdownMenu = document.getElementById('customerDropdownMenu');
        const dropdownList = document.getElementById('customerDropdownList');
        const clearBtn = document.getElementById('clearCustomerBtn');
        const wrapper = document.getElementById('customerSelectorWrapper');

        if (!searchInput || !hiddenInput || !dropdownMenu || !dropdownList) return;

        function renderDropdown(filterText = '') {
            dropdownList.innerHTML = '';
            const query = filterText.toLowerCase().trim();
            const filtered = customersList.filter(c => {
                if (!query) return true;
                const name = (c.customer_name || '').toLowerCase();
                const gstin = (c.gstin || '').toLowerCase();
                const lic = (c.licence_number || '').toLowerCase();
                const mobile = (c.mobile || '').toLowerCase();
                const state = (c.state || '').toLowerCase();
                return name.includes(query) || gstin.includes(query) || lic.includes(query) || mobile.includes(query) || state.includes(query);
            });

            if (filtered.length === 0) {
                dropdownList.innerHTML = `
                    <div style="padding: 12px; color: #94a3b8; text-align: center; font-size: 0.9rem;">No matching customers found</div>
                    <div style="padding: 10px 14px; border-top: 1px solid #e2e8f0; background: #f8fafc; text-align: center; font-weight: 600; cursor: pointer; color: #2563eb;" onclick="window.open('/customers', '_blank')">
                        ➕ Add New Party / Customer
                    </div>
                `;
                return;
            }

            filtered.forEach(c => {
                const item = document.createElement('div');
                item.className = 'customer-option-item';
                item.dataset.id = c.id;
                item.style.cssText = 'padding: 10px 14px; border-bottom: 1px solid #f1f5f9; cursor: pointer; transition: background 0.15s ease;';
                if (hiddenInput.value == c.id) {
                    item.style.background = '#eff6ff';
                    item.style.borderLeft = '4px solid #2563eb';
                }

                const licStr = c.licence_number ? `📜 <strong>Lic:</strong> ${c.licence_number}` : '';
                const gstStr = c.gstin ? `🏛️ <strong>GSTIN:</strong> ${c.gstin}` : '🏛️ Unregistered';
                const stateStr = c.state ? `📍 <strong>State:</strong> ${c.state}` : '';

                const metaParts = [licStr, gstStr, stateStr].filter(Boolean).join(' &nbsp;•&nbsp; ');

                item.innerHTML = `
                    <div style="font-weight: 600; color: #0f172a; font-size: 0.95rem;">${c.customer_name}</div>
                    <div style="font-size: 0.82rem; color: #64748b; margin-top: 2px;">${metaParts}</div>
                `;

                item.addEventListener('mouseenter', () => {
                    if (hiddenInput.value != c.id) item.style.background = '#f8fafc';
                });
                item.addEventListener('mouseleave', () => {
                    if (hiddenInput.value != c.id) item.style.background = '#ffffff';
                });

                item.addEventListener('click', (e) => {
                    e.stopPropagation();
                    selectCustomer(c);
                });

                dropdownList.appendChild(item);
            });

            // Footer option to add new party
            const footerOption = document.createElement('div');
            footerOption.style.cssText = 'padding: 10px 14px; border-top: 1px solid #e2e8f0; background: #f8fafc; text-align: center; font-weight: 600; cursor: pointer; color: #2563eb; position: sticky; bottom: 0;';
            footerOption.innerHTML = '➕ Add New Party / Customer';
            footerOption.addEventListener('click', (e) => {
                e.stopPropagation();
                window.open('/customers', '_blank');
            });
            dropdownList.appendChild(footerOption);
        }

        function selectCustomer(customer) {
            hiddenInput.value = customer.id;
            searchInput.value = customer.customer_name;
            if (clearBtn) clearBtn.style.display = 'block';
            dropdownMenu.style.display = 'none';
            handleCustomerChangeById(customer.id);
        }

        searchInput.addEventListener('focus', () => {
            renderDropdown(searchInput.value);
            dropdownMenu.style.display = 'block';
        });

        searchInput.addEventListener('input', () => {
            if (hiddenInput.value) {
                hiddenInput.value = '';
                if (clearBtn) clearBtn.style.display = 'none';
                handleCustomerChangeById(null);
            }
            renderDropdown(searchInput.value);
            dropdownMenu.style.display = 'block';
        });

        if (clearBtn) {
            clearBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                hiddenInput.value = '';
                searchInput.value = '';
                clearBtn.style.display = 'none';
                handleCustomerChangeById(null);
                renderDropdown('');
                dropdownMenu.style.display = 'block';
                searchInput.focus();
            });
        }

        document.addEventListener('click', (e) => {
            if (wrapper && !wrapper.contains(e.target)) {
                dropdownMenu.style.display = 'none';
            }
        });
    }

    function selectCustomerById(custId) {
        const hiddenInput = document.getElementById('customerId');
        const searchInput = document.getElementById('customerSearchInput');
        const clearBtn = document.getElementById('clearCustomerBtn');
        const customer = customersList.find(c => c.id == custId);

        if (customer) {
            if (hiddenInput) hiddenInput.value = customer.id;
            if (searchInput) searchInput.value = customer.customer_name;
            if (clearBtn) clearBtn.style.display = 'block';
            handleCustomerChangeById(customer.id);
        }
    }

    function handleCustomerChangeById(custId) {
        const card = document.getElementById('customerSummaryCard');
        
        if (!custId) {
            if (card) card.style.display = 'none';
            return;
        }

        const customer = customersList.find(c => c.id == custId);
        if (customer) {
            if (card) {
                card.style.display = 'block';
                document.getElementById('custCardName').textContent = customer.customer_name;
                document.getElementById('custCardLicence').textContent = customer.licence_number || 'N/A';
                document.getElementById('custCardGstin').textContent = customer.gstin || 'Unregistered';
                document.getElementById('custCardState').textContent = customer.state || 'N/A';
                document.getElementById('custCardAddress').textContent = `${customer.address_line1 || ''} ${customer.address_line2 || ''} ${customer.city || ''} ${customer.pincode || ''}`.trim() || 'No address stored';
                const editLink = document.getElementById('editCustLink');
                if (editLink) editLink.href = `/customers/${customer.id}/edit`;
            }

            if (businessDetails && (customer.state || customer.state_code) && (businessDetails.state || businessDetails.state_code)) {
                const taxModeSelect = document.getElementById('taxMode');
                const isSameState = (customer.state && businessDetails.state && customer.state.trim().toLowerCase() === businessDetails.state.trim().toLowerCase()) ||
                                    (customer.state_code && businessDetails.state_code && customer.state_code === businessDetails.state_code);
                if (isSameState) {
                    taxModeSelect.value = "CGST_SGST";
                } else {
                    taxModeSelect.value = "IGST";
                }
                calculateSummary();
            }
        }
    }

    function updateLineItemSerialNumbers() {
        const rows = document.querySelectorAll('#lineItemsBody .line-item-row');
        rows.forEach((row, index) => {
            const snoCell = row.querySelector('.item-sno');
            if (snoCell) snoCell.textContent = index + 1;
        });
    }

    function addLineItem() {
        const tbody = document.getElementById('lineItemsBody');
        const template = document.getElementById('lineItemTemplate');
        const clone = template.content.cloneNode(true);
        const row = clone.querySelector('tr');

        const inputsToListen = row.querySelectorAll('.item-desc, .item-cat, .item-hsn, .item-qty, .item-rate');
        inputsToListen.forEach(input => {
            input.addEventListener('input', calculateSummary);
        });

        row.querySelector('.remove-item-btn').addEventListener('click', () => {
            row.remove();
            updateLineItemSerialNumbers();
            calculateSummary();
        });

        tbody.appendChild(row);
        updateLineItemSerialNumbers();
    }

    function addLineItemWithData(itemData) {
        const tbody = document.getElementById('lineItemsBody');
        const template = document.getElementById('lineItemTemplate');
        const clone = template.content.cloneNode(true);
        const row = clone.querySelector('tr');

        if (itemData.description) row.querySelector('.item-desc').value = itemData.description;
        if (itemData.cat) row.querySelector('.item-cat').value = itemData.cat;
        if (itemData.hsn_sac) row.querySelector('.item-hsn').value = itemData.hsn_sac;
        if (itemData.quantity) row.querySelector('.item-qty').value = parseFloat(itemData.quantity);
        if (itemData.rate) row.querySelector('.item-rate').value = parseFloat(itemData.rate);

        const inputsToListen = row.querySelectorAll('.item-desc, .item-cat, .item-hsn, .item-qty, .item-rate');
        inputsToListen.forEach(input => {
            input.addEventListener('input', calculateSummary);
        });

        row.querySelector('.remove-item-btn').addEventListener('click', () => {
            row.remove();
            updateLineItemSerialNumbers();
            calculateSummary();
        });

        tbody.appendChild(row);
        updateLineItemSerialNumbers();
    }

    function getNumVal(el) {
        if (!el) return 0;
        if (el.value !== '' && el.value !== undefined) {
            const val = parseFloat(el.value);
            return isNaN(val) ? 0 : val;
        }
        if (el.placeholder !== '' && el.placeholder !== undefined) {
            const val = parseFloat(el.placeholder);
            return isNaN(val) ? 0 : val;
        }
        return 0;
    }

    function calculateSummary() {
        const rows = document.querySelectorAll('#lineItemsBody .line-item-row');
        let totalQty = 0;
        let totalTaxable = 0;
        const taxMode = document.getElementById('taxMode').value;
        const cgstRate = getNumVal(document.getElementById('cgstPercent'));
        const sgstRate = getNumVal(document.getElementById('sgstPercent'));
        const igstRate = getNumVal(document.getElementById('igstPercent'));
        
        rows.forEach(row => {
            const qty = getNumVal(row.querySelector('.item-qty'));
            const rate = getNumVal(row.querySelector('.item-rate'));

            totalQty += qty;
            const amount = qty * rate;
            row.querySelector('.item-amount').textContent = amount.toFixed(2);

            totalTaxable += amount;
        });

        let cgstAmount = 0, sgstAmount = 0, igstAmount = 0;

        if (taxMode === 'CGST_SGST') {
            cgstAmount = (totalTaxable * cgstRate) / 100;
            sgstAmount = (totalTaxable * sgstRate) / 100;
        } else {
            igstAmount = (totalTaxable * igstRate) / 100;
        }

        const subtotal = totalTaxable;
        const grandTotal = totalTaxable + cgstAmount + sgstAmount + igstAmount;

        const summaryTotalQtyEl = document.getElementById('summaryTotalQty');
        if (summaryTotalQtyEl) {
            summaryTotalQtyEl.textContent = Number.isInteger(totalQty) ? totalQty.toString() : totalQty.toFixed(2);
        }

        document.getElementById('summaryTaxable').textContent = '₹' + totalTaxable.toFixed(2);
        
        if (taxMode === 'CGST_SGST') {
            document.querySelector('.cgst-row').style.display = 'flex';
            document.querySelector('.sgst-row').style.display = 'flex';
            document.querySelector('.igst-row').style.display = 'none';
            document.getElementById('summaryCgst').textContent = '₹' + cgstAmount.toFixed(2);
            document.getElementById('summarySgst').textContent = '₹' + sgstAmount.toFixed(2);
        } else {
            document.querySelector('.cgst-row').style.display = 'none';
            document.querySelector('.sgst-row').style.display = 'none';
            document.querySelector('.igst-row').style.display = 'flex';
            document.getElementById('summaryIgst').textContent = '₹' + igstAmount.toFixed(2);
        }
        
        document.getElementById('summarySubtotal').textContent = '₹' + subtotal.toFixed(2);
        const roundOffEl = document.getElementById('summaryRoundOff');
        if (roundOffEl) roundOffEl.textContent = '₹0.00';
        document.getElementById('summaryGrandTotal').textContent = '₹' + grandTotal.toFixed(2);
    }

    async function saveDraft() {
        if (!document.getElementById('invoiceForm').reportValidity()) return;

        const taxMode = document.getElementById('taxMode').value;
        const cgstRate = getNumVal(document.getElementById('cgstPercent'));
        const sgstRate = getNumVal(document.getElementById('sgstPercent'));
        const igstRate = getNumVal(document.getElementById('igstPercent'));
        const totalGstRate = taxMode === 'CGST_SGST' ? (cgstRate + sgstRate) : igstRate;

        const data = {
            customer_id: document.getElementById('customerId').value ? parseInt(document.getElementById('customerId').value) : null,
            invoice_date: document.getElementById('invoiceDate').value,
            tax_mode: taxMode,
            reverse_charge: document.getElementById('reverseCharge').checked,
            notes: document.getElementById('notes').value,
            terms: document.getElementById('terms').value,
            items: []
        };

        const rows = document.querySelectorAll('#lineItemsBody .line-item-row');
        if (rows.length === 0) {
            UI.showToast('Please add at least one line item', 'error');
            return;
        }

        rows.forEach(row => {
            const pIdEl = row.querySelector('.product-select');
            const pId = pIdEl ? pIdEl.value : null;
            const catInput = row.querySelector('.item-cat');
            const qty = getNumVal(row.querySelector('.item-qty'));
            const rate = getNumVal(row.querySelector('.item-rate'));
            data.items.push({
                product_id: pId ? parseInt(pId) : null,
                description: row.querySelector('.item-desc').value,
                cat: catInput ? catInput.value : '',
                hsn_sac: row.querySelector('.item-hsn').value,
                quantity: qty,
                unit: '',
                rate: rate,
                discount_amount: 0,
                gst_rate: totalGstRate
            });
        });

        try {
            let res;
            if (editingInvoiceId) {
                res = await API.put(`/api/invoices/${editingInvoiceId}`, data);
                UI.showToast('Invoice draft updated!', 'success');
            } else {
                res = await API.post('/api/invoices', data);
                UI.showToast('Invoice draft saved!', 'success');
            }
            setTimeout(() => {
                window.location.href = `/invoices/${res.id}`;
            }, 1000);
        } catch (e) {
            UI.showToast(e.message || 'Error saving invoice', 'error');
        }
    }


    // --- History Logic ---
    let currentPage = 1;

    function initHistory() {
        document.getElementById('searchInvoice').addEventListener('input', () => { currentPage=1; loadInvoices(); });
        document.getElementById('filterStatus').addEventListener('change', () => { currentPage=1; loadInvoices(); });
        document.getElementById('refreshBtn').addEventListener('click', loadInvoices);
        loadInvoices();
    }

    async function loadInvoices() {
        const tbody = document.getElementById('invoicesBody');
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">Loading...</td></tr>';
        
        try {
            const status = document.getElementById('filterStatus').value;
            // The API might support search, status, page, limit
            let url = `/api/invoices?page=${currentPage}&limit=10`;
            if (status) url += `&status=${status}`;
            
            const res = await API.get(url);
            
            tbody.innerHTML = '';
            if (res.items.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center">No invoices found.</td></tr>';
                renderPagination(1, 1);
                return;
            }

            res.items.forEach(inv => {
                const tr = document.createElement('tr');
                const editBtnHtml = inv.status === 'DRAFT'
                    ? `<a href="/invoices/${inv.id}/edit" class="btn btn-sm btn-primary" style="background: #2563eb; color: #ffffff; border: none; font-weight: 500;">Edit</a>`
                    : '';
                const custName = (inv.customer_snapshot && inv.customer_snapshot.customer_name) 
                    || (inv.customer && inv.customer.customer_name) 
                    || 'N/A';
                tr.innerHTML = `
                    <td style="text-align: left; vertical-align: middle;">${inv.invoice_date}</td>
                    <td style="text-align: left; vertical-align: middle;">${inv.invoice_number || '<i>Draft</i>'}</td>
                    <td style="text-align: left; vertical-align: middle; font-weight: 500;">${Utils.escapeHtml(custName)}</td>
                    <td style="text-align: center; vertical-align: middle;"><span class="badge badge-${inv.status.toLowerCase()}">${inv.status}</span></td>
                    <td style="text-align: right; vertical-align: middle; padding-right: 1rem; font-variant-numeric: tabular-nums; font-weight: 600;">₹${parseFloat(inv.grand_total).toFixed(2)}</td>
                    <td style="text-align: right; vertical-align: middle; padding-right: 1rem; white-space: nowrap;">
                        <div style="display: inline-flex; gap: 0.35rem; align-items: center; justify-content: flex-end;">
                            ${editBtnHtml}
                            <a href="/invoices/${inv.id}" class="btn btn-sm btn-secondary">View</a>
                            <button onclick="InvoiceManager.deleteInvoice(${inv.id}, '${Utils.escapeHtml(inv.invoice_number || 'Draft')}')" class="btn btn-sm btn-danger" style="background: #ef4444; color: #ffffff; border: none;">Delete</button>
                        </div>
                    </td>
                `;
                tbody.appendChild(tr);
            });
            renderPagination(res.page, res.pages);
        } catch (e) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Failed to load invoices</td></tr>';
        }
    }

    function renderPagination(page, pages) {
        const container = document.getElementById('pagination');
        container.innerHTML = '';
        if (pages <= 1) return;

        for (let i = 1; i <= pages; i++) {
            const btn = document.createElement('button');
            btn.className = `btn btn-sm ${i === page ? 'btn-primary' : 'btn-secondary'}`;
            btn.textContent = i;
            btn.addEventListener('click', () => {
                currentPage = i;
                loadInvoices();
            });
            container.appendChild(btn);
        }
    }

    // --- Detail Logic ---
    async function initDetail(id) {
        try {
            const invoice = await API.get(`/api/invoices/${id}`);
            renderInvoiceDocument(invoice);
            
            // Buttons logic
            if (invoice.status === 'DRAFT') {
                const btnEdit = document.getElementById('btnEditInvoice');
                if (btnEdit) {
                    btnEdit.style.display = 'inline-block';
                    btnEdit.onclick = () => {
                        window.location.href = `/invoices/${id}/edit`;
                    };
                }
                const btnFinalize = document.getElementById('btnFinalize');
                if (btnFinalize) {
                    btnFinalize.style.display = 'inline-block';
                    btnFinalize.onclick = async () => {
                        if (confirm('Are you sure you want to finalize this invoice? Once finalized, it cannot be edited.')) {
                            try {
                                await API.post(`/api/invoices/${id}/finalize`);
                                if (typeof UI !== 'undefined' && UI.showToast) UI.showToast('Invoice finalized', 'success');
                                window.location.reload();
                            } catch(e) { if (typeof UI !== 'undefined' && UI.showToast) UI.showToast(e.message, 'error'); }
                        }
                    };
                }
            } else if (invoice.status === 'FINALIZED') {
                const btnCancel = document.getElementById('btnCancel');
                if (btnCancel) {
                    btnCancel.style.display = 'inline-block';
                    btnCancel.onclick = async () => {
                        if (confirm('Are you sure you want to cancel this invoice?')) {
                            try {
                                await API.post(`/api/invoices/${id}/cancel`);
                                if (typeof UI !== 'undefined' && UI.showToast) UI.showToast('Invoice cancelled', 'success');
                                window.location.reload();
                            } catch(e) { if (typeof UI !== 'undefined' && UI.showToast) UI.showToast(e.message, 'error'); }
                        }
                    };
                }
            }

            document.getElementById('btnDelete')?.addEventListener('click', () => {
                deleteInvoice(id, invoice.invoice_number || 'Draft');
            });

            document.getElementById('btnDownloadPdf')?.addEventListener('click', () => {
                const token = API.getToken();
                window.open(`/api/invoices/${id}/pdf?token=${token}`, '_blank');
            });

        } catch (e) {
            console.error('Error loading invoice detail:', e);
            if (typeof Toast !== 'undefined') Toast.error('Error loading invoice details');
            else if (typeof UI !== 'undefined' && UI.showToast) UI.showToast('Error loading invoice details', 'error');
        }
    }

    async function deleteInvoice(id, invNum) {
        if (!confirm(`Are you sure you want to permanently delete invoice "${invNum}"?`)) return;
        try {
            await API.delete(`/api/invoices/${id}`);
            if (typeof Toast !== 'undefined') Toast.success('Invoice deleted successfully');
            if (window.location.pathname.includes('/invoices/')) {
                window.location.href = '/invoices';
            } else {
                loadInvoices();
            }
        } catch (error) {
            if (typeof Toast !== 'undefined') Toast.error(error.message || 'Failed to delete invoice');
        }
    }

    function renderInvoiceDocument(inv) {
        const setElText = (id, text) => {
            const el = document.getElementById(id);
            if (el) el.textContent = text;
        };

        setElText('headerInvoiceNumber', inv.invoice_number || 'Draft');
        setElText('lblInvoiceNumber', inv.invoice_number || 'Draft');
        setElText('lblInvoiceDate', inv.invoice_date);
        setElText('lblReverseCharge', inv.reverse_charge ? 'Yes' : 'No');
        
        if (inv.status === 'CANCELLED') {
            const docTitleEl = document.getElementById('docTitle');
            if (docTitleEl) {
                docTitleEl.textContent = 'CANCELLED INVOICE';
                docTitleEl.style.color = 'red';
            }
        }

        // Seller
        const s = inv.seller_snapshot || inv.business;
        if (s) {
            setElText('sellerName', s.trade_name || s.legal_name || s.business_name || 'Company Name');
            setElText('sellerAddress', `${s.address_line1 || ''} ${s.address_line2 || ''}`.trim() || '-');
            setElText('sellerCityState', `${s.city || ''}, ${s.state || ''} - ${s.pincode || ''}`);
            setElText('sellerGstin', s.gstin || '-');
            setElText('sellerLicence', s.licence_number || '-');
            setElText('sellerEmail', s.email || '-');
            setElText('sellerPhone', s.phone || '-');
            setElText('sigCompanyName', s.trade_name || s.legal_name || s.business_name || 'Company Name');
            
            setElText('bankName', s.bank_name || '-');
            setElText('bankAcNo', s.bank_account_number || '-');
            setElText('bankIfsc', s.bank_ifsc || '-');
        }

        // Buyer
        const b = inv.customer_snapshot || inv.customer;
        if (b) {
            setElText('buyerName', b.customer_name || 'Customer Name');
            setElText('buyerAddress', `${b.address_line1 || ''} ${b.address_line2 || ''}`.trim() || '-');
            setElText('buyerCityState', `${b.city || ''}, ${b.state || ''} - ${b.pincode || ''}`);
            setElText('buyerGstin', b.gstin || '-');
            setElText('buyerLicence', b.licence_number || '-');
            setElText('buyerStateCode', b.state_code || '-');
        }

        // Items
        const tbody = document.getElementById('invoiceItemsBody');
        if (tbody) {
            tbody.innerHTML = '';
            (inv.items || []).forEach((item, index) => {
                const tr = document.createElement('tr');
                const qty = parseFloat(item.quantity) || 0;
                const rate = parseFloat(item.rate) || 0;
                const amount = qty * rate;
                const formattedQty = Number.isInteger(qty) ? qty.toString() : qty.toFixed(2);
                tr.innerHTML = `
                    <td style="text-align: center;">${index + 1}</td>
                    <td>${item.description}</td>
                    <td style="text-align: center;">${item.cat || '-'}</td>
                    <td style="text-align: center;">${item.hsn_sac || '-'}</td>
                    <td class="text-right">${formattedQty}</td>
                    <td class="text-right">${rate.toFixed(2)}</td>
                    <td class="text-right">${amount.toFixed(2)}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        // Totals
        let totalQty = 0;
        (inv.items || []).forEach(item => {
            totalQty += parseFloat(item.quantity) || 0;
        });
        
        setElText('lblTotalQty', Number.isInteger(totalQty) ? totalQty.toString() : totalQty.toFixed(2));
        setElText('lblSubtotal', parseFloat(inv.subtotal).toFixed(2));
        setElText('lblTaxable', parseFloat(inv.taxable_amount).toFixed(2));
        setElText('lblRoundOff', parseFloat(inv.round_off).toFixed(2));
        setElText('lblGrandTotal', parseFloat(inv.grand_total).toFixed(2));
        
        let cgstRate = 0, sgstRate = 0, igstRate = 0;
        const taxable = parseFloat(inv.taxable_amount) || 0;
        if (taxable > 0) {
            cgstRate = (parseFloat(inv.cgst_amount) / taxable) * 100;
            sgstRate = (parseFloat(inv.sgst_amount) / taxable) * 100;
            igstRate = (parseFloat(inv.igst_amount) / taxable) * 100;
        } else if (inv.items && inv.items.length > 0) {
            const firstItemGst = parseFloat(inv.items[0].gst_rate) || 0;
            cgstRate = firstItemGst / 2;
            sgstRate = firstItemGst / 2;
            igstRate = firstItemGst;
        }

        const formatPercent = (val) => {
            const rounded = Math.round(val * 100) / 100;
            return Number.isInteger(rounded) ? rounded.toString() : rounded.toFixed(1);
        };

        const rowCgst = document.getElementById('rowCgst');
        const rowSgst = document.getElementById('rowSgst');
        const rowIgst = document.getElementById('rowIgst');

        if (inv.tax_mode === 'CGST_SGST') {
            if (rowCgst) rowCgst.style.display = '';
            if (rowSgst) rowSgst.style.display = '';
            if (rowIgst) rowIgst.style.display = 'none';
            setElText('lblCgstLabel', `CGST (${formatPercent(cgstRate)}%):`);
            setElText('lblSgstLabel', `SGST (${formatPercent(sgstRate)}%):`);
            setElText('lblCgst', parseFloat(inv.cgst_amount).toFixed(2));
            setElText('lblSgst', parseFloat(inv.sgst_amount).toFixed(2));
        } else {
            if (rowCgst) rowCgst.style.display = 'none';
            if (rowSgst) rowSgst.style.display = 'none';
            if (rowIgst) rowIgst.style.display = '';
            setElText('lblIgstLabel', `IGST (${formatPercent(igstRate)}%):`);
            setElText('lblIgst', parseFloat(inv.igst_amount).toFixed(2));
        }

        if (inv.notes) {
            const notesBlock = document.getElementById('notesBlock');
            if (notesBlock) notesBlock.style.display = 'block';
            setElText('lblNotes', inv.notes);
        }
        if (inv.terms) {
            const termsBlock = document.getElementById('termsBlock');
            if (termsBlock) termsBlock.style.display = 'block';
            setElText('lblTerms', inv.terms);
        }
    }

    return {
        initCreate,
        initHistory,
        initDetail,
        deleteInvoice
    };
})();
