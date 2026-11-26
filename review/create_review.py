import html
from pathlib import Path

import pandas as pd

source = Path("data/constitutional_candidates_2015_2025.csv")
output = Path("review/constitutional_review.html")

df = pd.read_csv(source).fillna("")

rows = []

for _, row in df.iterrows():
    key = html.escape(str(row["path"]), quote=True)

    cells = "".join(
        f"<td>{html.escape(str(row[column]))}</td>"
        for column in ["year", "title", "score", "matched_terms", "review_status"]
    )

    rows.append(f"""
    <tr data-key="{key}">
        {cells}
        <td>
            <select class="decision">
                <option value="unreviewed">Unreviewed</option>
                <option value="include">Include</option>
                <option value="exclude">Exclude</option>
                <option value="needs_further_review">Needs further review</option>
            </select>
        </td>
    </tr>
    """)

page = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>PrecedentPal Candidate Review</title>
<style>
body { font-family: Arial; margin: 25px; }
input { padding: 10px; width: 350px; margin-bottom: 15px; }
button { padding: 10px 15px; margin: 10px 0; cursor: pointer; }
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
th { background: #eee; position: sticky; top: 0; }
tr:nth-child(even) { background: #f8f8f8; }
</style>
</head>
<body>

<h2>PrecedentPal — Constitutional Candidate Review</h2>
<p>Total candidates: COUNT</p>
<p id="progress">Loading saved decisions...</p>

<input id="search" placeholder="Search case names or matched terms...">
<br>
<button id="export">Export reviewed CSV</button>

<table>
<thead>
<tr>
<th>Year</th><th>Case</th><th>Score</th>
<th>Matched terms</th><th>Screening tier</th><th>Your decision</th>
</tr>
</thead>
<tbody>
ROWS
</tbody>
</table>

<script>
const storagePrefix = "precedentpal-review:";

function updateProgress() {
    const selects = document.querySelectorAll(".decision");
    let reviewed = 0;

    selects.forEach(select => {
        if (select.value !== "unreviewed") reviewed++;
    });

    document.getElementById("progress").innerText =
        `Reviewed: ${reviewed} / ${selects.length}`;
}

document.querySelectorAll("tbody tr").forEach(row => {
    const key = storagePrefix + row.dataset.key;
    const select = row.querySelector(".decision");
    const saved = localStorage.getItem(key);

    if (saved) select.value = saved;

    select.addEventListener("change", () => {
        localStorage.setItem(key, select.value);
        updateProgress();
    });
});

document.getElementById("search").addEventListener("input", function() {
    const query = this.value.toLowerCase();

    document.querySelectorAll("tbody tr").forEach(row => {
        row.style.display =
            row.innerText.toLowerCase().includes(query) ? "" : "none";
    });
});

document.getElementById("export").addEventListener("click", function() {
    const data = [[
        "year", "title", "score", "matched_terms",
        "review_status", "review_decision", "path"
    ]];

    document.querySelectorAll("tbody tr").forEach(row => {
        const cells = row.querySelectorAll("td");
        data.push([
            cells[0].innerText,
            cells[1].innerText,
            cells[2].innerText,
            cells[3].innerText,
            cells[4].innerText,
            cells[5].querySelector("select").value,
            row.dataset.key
        ]);
    });

    const csv = data.map(line =>
        line.map(value =>
            '"' + String(value).replace(/"/g, '""') + '"'
        ).join(",")
    ).join("\\r\\n");

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "constitutional_reviewed.csv";
    link.click();
    URL.revokeObjectURL(url);
});

updateProgress();
</script>
</body>
</html>
"""

page = page.replace("COUNT", str(len(df)))
page = page.replace("ROWS", "\n".join(rows))

output.write_text(page, encoding="utf-8")
print(f"Created {output} with {len(df)} candidates.")
