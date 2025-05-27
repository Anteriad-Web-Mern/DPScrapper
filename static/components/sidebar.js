class AppSidebar extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
            <nav class="h-screen w-60 bg-background/80 border-r border-border flex flex-col gap-2 py-6 px-4 backdrop-blur-md shadow-xl transition-shadow duration-300">
                <div class="mb-4 text-lg font-semibold text-primary">Menu</div>
                <a href="/dashboard" class="block rounded-md px-3 py-2 hover:bg-accent hover:text-accent-foreground transition-colors font-medium focus:ring-2 focus:ring-primary">Dashboard</a>
                <a href="/scraping-tasks" class="block rounded-md px-3 py-2 hover:bg-accent hover:text-accent-foreground transition-colors font-medium focus:ring-2 focus:ring-primary">Scraping Tasks</a>
                <a href="/results" class="block rounded-md px-3 py-2 hover:bg-accent hover:text-accent-foreground transition-colors font-medium focus:ring-2 focus:ring-primary">Results</a>
                <a href="/analytics" class="block rounded-md px-3 py-2 hover:bg-accent hover:text-accent-foreground transition-colors font-medium focus:ring-2 focus:ring-primary">Analytics</a>
                <a href="/logs" class="block rounded-md px-3 py-2 hover:bg-accent hover:text-accent-foreground transition-colors font-medium focus:ring-2 focus:ring-primary">Logs</a>
                <a href="/user-management" class="block rounded-md px-3 py-2 hover:bg-accent hover:text-accent-foreground transition-colors font-medium focus:ring-2 focus:ring-primary">User Management</a>
                <a href="/settings" class="block rounded-md px-3 py-2 hover:bg-accent hover:text-accent-foreground transition-colors font-medium focus:ring-2 focus:ring-primary">Settings</a>
                <a href="/bulk-add-user" class="block rounded-md px-3 py-2 hover:bg-accent hover:text-accent-foreground transition-colors">Bulk Add User</a>
            </nav>
        `;
    }
}

customElements.define("app-sidebar", AppSidebar);
