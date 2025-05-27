document.addEventListener("DOMContentLoaded", () => {
    const logsTable = document.querySelector("#logsTable tbody");

    // Sample logs (Replace with API call)
    let logs = [
        { timestamp: "2025-04-02 14:30", user: "Admin", action: "Deleted a user", status: "Success" },
        { timestamp: "2025-04-02 14:00", user: "John", action: "Started Scraping Task", status: "Pending" },
        { timestamp: "2025-04-02 13:45", user: "Jane", action: "Updated Settings", status: "Success" }
    ];

    function renderLogs() {
        logsTable.innerHTML = "";
        logs.forEach(log => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${log.timestamp}</td>
                <td>${log.user}</td>
                <td>${log.action}</td>
                <td>${log.status}</td>
            `;
            logsTable.appendChild(row);
        });
    }

    renderLogs();
});
