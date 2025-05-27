class AppHeader extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
            <header class="w-full flex items-center justify-between bg-gradient-to-r from-background via-accent to-background border-b border-border px-8 py-4 text-foreground shadow-lg transition-shadow duration-300">
                <div class="text-2xl font-bold tracking-tight">Scraping Dashboard</div>
                <nav class="flex gap-6 items-center">
                    <a href="/dashboard" class="text-muted-foreground hover:text-primary transition-colors font-medium hover:underline underline-offset-4">Dashboard</a>
                    <a href="/settings" class="text-muted-foreground hover:text-primary transition-colors font-medium hover:underline underline-offset-4">Settings</a>
                    <a href="#" class="text-muted-foreground hover:text-destructive transition-colors font-medium hover:underline underline-offset-4">Logout</a>
                </nav>
            </header>
        `;
    }
}

customElements.define("app-header", AppHeader);
