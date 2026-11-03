document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
});

async function initDashboard() {
    const statsGrid = document.getElementById('statsGrid');
    const recentInvoicesBody = document.getElementById('recentInvoicesBody');
    
    // Show skeletons
    statsGrid.innerHTML = `
        <div class="stat-card skeleton-box" style="height: 100px;"></div>
        <div class="stat-card skeleton-box" style="height: 100px;"></div>
    `;
    
    Loading.skeleton(recentInvoicesBody, 5);

    try {
        // Fetch dashboard summary
        const summary = await API.get('/api/dashboard/summary');
        
        // Render Stats
        renderStats(summary);
        
        // Render Recent Invoices from summary
        renderRecentInvoices(summary.recent_invoices);

    } catch (error) {
        if (typeof Toast !== 'undefined') Toast.error('Failed to load dashboard data');
        console.error('Dashboard error:', error);
        
        statsGrid.innerHTML = '<div style="grid-column: 1/-1; text-align:center;">Failed to load stats.</div>';
        recentInvoicesBody.innerHTML = '<tr><td colspan="5" style="text-align:center;">Failed to load invoices.</td></tr>';
    }
}

function renderStats(data) {
    const statsGrid = document.getElementById('statsGrid');
    statsGrid.innerHTML = `
        <div class="stat-card" style="background: #FFFFFF; padding: 1.25rem 1.5rem; border-radius: var(--radius-lg); border: 1px solid var(--color-border); box-shadow: var(--shadow-sm);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <span style="color: var(--color-text-secondary); font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em;">Total Invoices</span>
                <span style="font-size: 1.25rem;">📄</span>
            </div>
            <div style="font-size: 1.6rem; font-weight: 700; color: var(--color-text-primary); letter-spacing: -0.02em;">${data.total_invoices || 0}</div>
        </div>
        <div class="stat-card" style="background: #FFFFFF; padding: 1.25rem 1.5rem; border-radius: var(--radius-lg); border: 1px solid var(--color-border); box-shadow: var(--shadow-sm);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <span style="color: var(--color-text-secondary); font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em;">Customers</span>
                <span style="font-size: 1.25rem;">👥</span>
            </div>
            <div style="font-size: 1.6rem; font-weight: 700; color: var(--color-text-primary); letter-spacing: -0.02em;">${data.total_customers || 0}</div>
        </div>
    `;
}

function renderRecentInvoices(invoices) {
    const tbody = document.getElementById('recentInvoicesBody');
    tbody.innerHTML = '';
    
    if (!invoices || invoices.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; padding: 2rem; color: var(--color-text-secondary);">
                    No recent invoices found.
                </td>
            </tr>
        `;
        return;
    }
    
    invoices.forEach(inv => {
        const tr = document.createElement('tr');
        
        let badgeClass = 'badge-draft';
        if (inv.status === 'FINALIZED') badgeClass = 'badge-finalized';
        if (inv.status === 'CANCELLED') badgeClass = 'badge-cancelled';
        
        tr.innerHTML = `
            <td><a href="/invoices/${inv.id}" style="color: var(--color-primary); font-weight: 600;">${Utils.escapeHtml(inv.invoice_number || 'Draft')}</a></td>
            <td>${inv.invoice_date ? Utils.formatDate(inv.invoice_date) : '-'}</td>
            <td><strong>${Utils.escapeHtml(inv.customer_name || 'N/A')}</strong></td>
            <td style="text-align: right; font-weight: 600;">${Utils.formatCurrency(inv.grand_total)}</td>
            <td>
                <span class="badge ${badgeClass}">
                    ${Utils.escapeHtml(inv.status || 'DRAFT')}
                </span>
            </td>
        `;
        tbody.appendChild(tr);
    });
}
