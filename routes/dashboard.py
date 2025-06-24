from flask import Blueprint, render_template
from utils.db import get_mysql_conn

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    conn = get_mysql_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM domains")
    domain_stats = cursor.fetchall()
    conn.close()
    summary = {
        "total_users": sum(row[1] for row in domain_stats),
        "total_blogs": sum(row[2] for row in domain_stats),
        "total_resources": sum(row[3] for row in domain_stats),
        "total_thank_you": sum(row[4] for row in domain_stats),
    }
    analytics = {
        "domains": [row[0] for row in domain_stats],
        "users": [row[1] for row in domain_stats],
        "blogs": [row[2] for row in domain_stats],
        "resources": [row[3] for row in domain_stats],
        "thank_you": [row[4] for row in domain_stats],
    }
    return render_template("dashboard.html", domain_stats=domain_stats, summary=summary, analytics=analytics)
