class AppHeader extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: "open" });
    }

    connectedCallback() {
        this.shadowRoot.innerHTML = `
            <style>
                .header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    background: #1e293b;
                    color: white;
                    padding: 1rem 2rem;
                    font-size: 1.5rem;
                    font-weight: bold;
                }
                .logo {
                    font-size: 1.8rem;
                    font-weight: bold;
                }
                .nav-links {
                    display: flex;
                    gap: 1rem;
                }
                .nav-links a {
                    color: white;
                    text-decoration: none;
                    font-size: 1rem;
                    transition: 0.3s;
                }
                .nav-links a:hover {
                    text-decoration: underline;
                }
            </style>
            <header class="header">
                <div class="logo">Scraping Dashboard</div>
                <nav class="nav-links">
                    <a href="dashboard.html">Dashboard</a>
                    <a href="settings.html">Settings</a>
                    <a href="#">Logout</a>
                </nav>
            </header>
        `;
    }
}

customElements.define("app-header", AppHeader);
