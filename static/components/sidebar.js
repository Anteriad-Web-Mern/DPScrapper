class AppSidebar extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: "open" });
    }

    connectedCallback() {
        this.shadowRoot.innerHTML = `
            <style>
                .sidebar {
                    width: 250px;
                    height: 100vh;
                    background: #1e293b;
                    color: white;
                    display: flex;
                    flex-direction: column;
                    gap: 1rem;
                }
                .menu-item {
                    padding: 0.75rem;
                    cursor: pointer;
                    transition: background 0.3s;
                }
                .menu-item:hover {
                    background: #475569;
                }
                .menu-item a {
                    color: white;
                    text-decoration: none;
                    font-size: 1rem;
                    display: block;
                }
            </style>
           <nav class="sidebar">
                <div class="menu-item"><a href="/dashboard">Dashboard</a></div>
                <div class="menu-item"><a href="/scraping-tasks">Scraping Tasks</a></div>
                <div class="menu-item"><a href="/scraping-config">Scraping Config</a></div>
                <div class="menu-item"><a href="/results">Results</a></div>
                <div class="menu-item"><a href="/analytics">Analytics</a></div>
                <div class="menu-item"><a href="/reports">Reports</a></div>
                <div class="menu-item"><a href="/logs">Logs</a></div>
                <div class="menu-item"><a href="/history">History</a></div>
                <div class="menu-item"><a href="/data-export">Data Export</a></div>
                <div class="menu-item"><a href="/user-management">User Management</a></div>
                <div class="menu-item"><a href="/user-roles">User Roles</a></div>
                <div class="menu-item"><a href="/settings">Settings</a></div>
            </nav>
        `;
    }
}

customElements.define("app-sidebar", AppSidebar);
