class AppFooter extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
            <footer class="w-full bg-gradient-to-r from-background via-accent to-background border-t border-border text-muted-foreground text-center py-4 text-sm shadow-inner transition-shadow duration-300 hover:text-primary">
                &copy; ${new Date().getFullYear()} Scraping Dashboard. All rights reserved.
            </footer>
        `;
    }
}
customElements.define('app-footer', AppFooter);