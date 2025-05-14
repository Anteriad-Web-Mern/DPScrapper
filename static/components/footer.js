class AppFooter extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
            <style>
                .app-footer {
                    width: 100%;
                    background: #1e293b;
                    color: white;
                    text-align: center;
                    padding: 1rem 0;
                    position: fixed;
                    bottom: 0;
                    left: 0;
                    font-size: 0.9rem;
                }
            </style>
            <footer class="app-footer">
                <p>&copy; ${new Date().getFullYear()} Scraping Dashboard. All rights reserved.</p>
            </footer>
        `;
    }
}
customElements.define('app-footer', AppFooter);