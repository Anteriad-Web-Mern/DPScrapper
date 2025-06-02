document.getElementById('addUserBtn').onclick = function() {
    document.getElementById('addUserModal').style.display = 'block';
};

function closeModal() {
    document.getElementById('addUserModal').style.display = 'none';
}

document.getElementById('addUserForm').onsubmit = async function(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    // Log the data to the console to inspect it
    console.log('Data being sent:', data);

    const token = localStorage.getItem('authToken'); // Or however you store your token

    const res = await fetch('/api/add-user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}` // Add the token to the header
        },
        body: JSON.stringify(data)
    });

    if (res.ok) {
        closeModal();
        loadUsers();
    } else {
        // Log the error response from the server
        const errorText = await res.text();
        console.error('Failed to add user:', res.status, errorText);
        alert('Failed to add user. Check console for details.');
    }
};

document.getElementById('roleFilter').onchange = function() {
    loadUsers();
};

async function loadUsers() {
    const role = document.getElementById('roleFilter').value;
    const token = localStorage.getItem('authToken'); // Or however you store your token

    const res = await fetch('/api/users' + (role ? `?role=${role}` : ''), {
        headers: {
            'Authorization': `Bearer ${token}` // Add the token to the header
        }
    });
    const users = await res.json();
    const tbody = document.querySelector('#userTable tbody');
    tbody.innerHTML = '';
    users.forEach(u => {
        tbody.innerHTML += `<tr>
            <td>${u.id}</td>
            <td>${u.name}</td>
            <td>${u.email}</td>
            <td>${u.roles.join(', ')}</td>
            <td><!-- Actions here --></td>
        </tr>`;
    });
}

window.onload = loadUsers;