document.addEventListener("DOMContentLoaded", () => {
    const userTable = document.querySelector("#userTable tbody");
    const addUserBtn = document.getElementById("addUserBtn");

    // Sample users (Replace with API calls)
    let users = [
        { id: 1, name: "John Doe", email: "john@example.com", role: "Admin" },
        { id: 2, name: "Jane Smith", email: "jane@example.com", role: "Editor" }
    ];

    function renderUsers() {
        userTable.innerHTML = "";
        users.forEach(user => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${user.id}</td>
                <td>${user.name}</td>
                <td>${user.email}</td>
                <td>${user.role}</td>
                <td>
                    <button class="edit-btn" data-id="${user.id}">Edit</button>
                    <button class="delete-btn" data-id="${user.id}">Delete</button>
                </td>
            `;
            userTable.appendChild(row);
        });
    }

    // Handle delete user
    userTable.addEventListener("click", (e) => {
        if (e.target.classList.contains("delete-btn")) {
            const userId = e.target.dataset.id;
            users = users.filter(user => user.id != userId);
            renderUsers();
        }
    });

    // Add user event
    addUserBtn.addEventListener("click", () => {
        const newUser = {
            id: users.length + 1,
            name: "New User",
            email: "newuser@example.com",
            role: "Viewer"
        };
        users.push(newUser);
        renderUsers();
    });

    renderUsers(); // Initial render
});
