document.addEventListener('DOMContentLoaded', () => {
    // Check auth and role
    const profile = API.getProfile();
    if (!profile) {
        window.location.href = '/login';
        return;
    }

    if (profile.role !== 'admin') {
        showToast('Only admins can access user management', 'error');
        setTimeout(() => {
            window.location.href = '/dashboard';
        }, 1500);
        return;
    }

    loadUsers();

    document.getElementById('addUserBtn').addEventListener('click', openUserModal);
});

async function loadUsers() {
    try {
        const response = await API.get('/users');
        renderUsers(response.items);
    } catch (error) {
        showToast(error.message || 'Failed to load users', 'error');
        document.getElementById('usersTableBody').innerHTML = `
            <tr><td colspan="5" class="text-center text-danger">Failed to load users</td></tr>
        `;
    }
}

function renderUsers(users) {
    const tbody = document.getElementById('usersTableBody');
    const currentUser = API.getProfile();
    
    if (!users || users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">No users found</td></tr>';
        return;
    }

    tbody.innerHTML = users.map(user => `
        <tr>
            <td>${escapeHtml(user.name)} ${user.id === currentUser.id ? '(You)' : ''}</td>
            <td>${escapeHtml(user.email)}</td>
            <td>
                <span class="badge ${user.role === 'admin' ? 'badge-primary' : 'badge-secondary'}">
                    ${user.role.toUpperCase()}
                </span>
            </td>
            <td>
                <label class="switch">
                    <input type="checkbox" ${user.is_active ? 'checked' : ''} 
                           onchange="toggleUserStatus(${user.id}, this.checked)"
                           ${user.id === currentUser.id ? 'disabled' : ''}>
                    <span class="slider round"></span>
                </label>
            </td>
            <td>
                <button class="btn btn-sm btn-secondary" 
                        onclick="openRoleModal(${user.id}, '${user.role}')"
                        ${user.id === currentUser.id ? 'disabled' : ''}>
                    Edit Role
                </button>
            </td>
        </tr>
    `).join('');
}

function openUserModal() {
    document.getElementById('userForm').reset();
    document.getElementById('userModal').style.display = 'flex';
}

function closeUserModal() {
    document.getElementById('userModal').style.display = 'none';
}

async function saveUser() {
    const form = document.getElementById('userForm');
    if (!form.reportValidity()) return;

    const data = {
        name: document.getElementById('userName').value,
        email: document.getElementById('userEmail').value,
        password: document.getElementById('userPassword').value,
        role: document.getElementById('userRole').value
    };

    try {
        await API.post('/users', data);
        showToast('User created successfully', 'success');
        closeUserModal();
        loadUsers();
    } catch (error) {
        showToast(error.message || 'Failed to create user', 'error');
    }
}

function openRoleModal(userId, currentRole) {
    document.getElementById('editUserId').value = userId;
    document.getElementById('editUserRole').value = currentRole;
    document.getElementById('roleModal').style.display = 'flex';
}

function closeRoleModal() {
    document.getElementById('roleModal').style.display = 'none';
}

async function saveRole() {
    const userId = document.getElementById('editUserId').value;
    const role = document.getElementById('editUserRole').value;

    try {
        await API.patch(`/users/${userId}/role`, { role });
        showToast('Role updated successfully', 'success');
        closeRoleModal();
        loadUsers();
    } catch (error) {
        showToast(error.message || 'Failed to update role', 'error');
    }
}

async function toggleUserStatus(userId, isActive) {
    try {
        await API.patch(`/users/${userId}/status`, { is_active: isActive });
        showToast('Status updated successfully', 'success');
    } catch (error) {
        showToast(error.message || 'Failed to update status', 'error');
        loadUsers(); // reload to reset toggle state
    }
}
