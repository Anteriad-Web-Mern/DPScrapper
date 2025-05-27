document.addEventListener("DOMContentLoaded", () => {
    const reportsTable = document.querySelector("#reportsTable tbody");

    // Sample Reports Data (Replace with API call)
    let reports = [
        { date: "2025-04-02", task: "E-commerce Scraping", status: "Completed", records: 1200 },
        { date: "2025-04-01", task: "News Scraping", status: "Failed", records: 0 },
        { date: "2025-03-31", task: "Social Media Data", status: "Completed", records: 850 }
    ];

    function renderReports() {
        reportsTable.innerHTML = "";
        reports.forEach(report => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${report.date}</td>
                <td>${report.task}</td>
                <td>${report.status}</td>
                <td>${report.records}</td>
            `;
            reportsTable.appendChild(row);
        });
    }

    renderReports();

    // Charts Initialization
    const ctx1 = document.getElementById("scrapeTrendsChart").getContext("2d");
    new Chart(ctx1, {
        type: "line",
        data: {
            labels: ["Mar 25", "Mar 26", "Mar 27", "Mar 28", "Mar 29", "Mar 30", "Mar 31"],
            datasets: [{
                label: "Records Scraped",
                data: [500, 800, 1200, 1100, 1400, 1350, 1250],
                borderColor: "#4CAF50",
                fill: false
            }]
        },
        options: { responsive: true }
    });

    const ctx2 = document.getElementById("successRateChart").getContext("2d");
    new Chart(ctx2, {
        type: "doughnut",
        data: {
            labels: ["Success", "Failed"],
            datasets: [{
                data: [85, 15],
                backgroundColor: ["#4CAF50", "#F44336"]
            }]
        },
        options: { responsive: true }
    });
});
