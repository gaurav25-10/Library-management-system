(function () {
    "use strict";

    document.querySelectorAll(".needs-validation").forEach((form) => {
        form.addEventListener("submit", (event) => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add("was-validated");
        });
    });

    document.querySelectorAll("table.sortable").forEach((table) => {
        const headers = table.querySelectorAll("th");
        headers.forEach((header, index) => {
            header.addEventListener("click", () => {
                const tbody = table.querySelector("tbody");
                const rows = Array.from(tbody.querySelectorAll("tr"));
                const asc = header.dataset.sortDir !== "asc";
                rows.sort((a, b) => {
                    const left = a.children[index]?.innerText.trim().toLowerCase() || "";
                    const right = b.children[index]?.innerText.trim().toLowerCase() || "";
                    return asc ? left.localeCompare(right, undefined, { numeric: true }) : right.localeCompare(left, undefined, { numeric: true });
                });
                header.dataset.sortDir = asc ? "asc" : "desc";
                rows.forEach((row) => tbody.appendChild(row));
            });
        });
    });

    const issueChart = document.getElementById("issueChart");
    if (issueChart && window.Chart) {
        new Chart(issueChart, {
            type: "bar",
            data: {
                labels: ["Issued", "Returned", "Overdue"],
                datasets: [{
                    label: "Books",
                    data: [issueChart.dataset.issued, issueChart.dataset.returned, issueChart.dataset.overdue],
                    backgroundColor: ["#2563eb", "#059669", "#dc2626"],
                    borderRadius: 6
                }]
            },
            options: { responsive: true, plugins: { legend: { display: false } } }
        });
    }

    const categoryChart = document.getElementById("categoryChart");
    if (categoryChart && window.Chart) {
        new Chart(categoryChart, {
            type: "doughnut",
            data: {
                labels: JSON.parse(categoryChart.dataset.labels || "[]"),
                datasets: [{
                    data: JSON.parse(categoryChart.dataset.values || "[]"),
                    backgroundColor: ["#2563eb", "#059669", "#d97706", "#0891b2", "#7c3aed", "#dc2626"]
                }]
            },
            options: { responsive: true, plugins: { legend: { position: "bottom" } } }
        });
    }
})();
