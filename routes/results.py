from flask import Blueprint, render_template
from utils.db import get_mysql_conn
import analytics_report

results_bp = Blueprint('results', __name__)

@results_bp.route("/results")
def results_summary():
    conn = get_mysql_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT domain, users, blogs, resources, thank_you FROM domains")
    all_rows = cursor.fetchall()
    conn.close()

    summary_data = {
        "total_users": sum(row[1] for row in all_rows),
        "total_blogs": sum(row[2] for row in all_rows),
        "total_resources": sum(row[3] for row in all_rows),
        "total_thank_you": sum(row[4] for row in all_rows),
    }

    return render_template("results.html", all_results=all_rows, summary=summary_data)

@results_bp.route("/results/<domain>")
def results_for_domain(domain):
    conn = get_mysql_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT domain, users, blogs, resources, thank_you FROM domains WHERE domain = %s",
        (domain,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return render_template("results.html", result=None, error="Domain not found")

    result_data = {
        "domain": row[0],
        "users": row[1],
        "blogs": row[2],
        "resources": row[3],
        "thank_you": row[4],
    }

    analytics_data = analytics_report.report  # Assuming this is valid

    return render_template("results.html", result=result_data, analytics_data=analytics_data)
