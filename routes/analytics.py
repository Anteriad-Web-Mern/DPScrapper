from flask import Blueprint, request, jsonify, render_template
from utils.db import get_mysql_conn

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route("/analytics")
def analytics():
    # Fetch all domain data from the `domains` table
    conn = get_mysql_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT domain, users, blogs, resources, thank_you FROM domains")
    rows = cursor.fetchall()
    conn.close()

    # Prepare data for visualization
    domains = [row[0] for row in rows]
    users = [row[1] for row in rows]
    blogs = [row[2] for row in rows]
    resources = [row[3] for row in rows]
    thank_you = [row[4] for row in rows]

    analytics_data = {
        "domains": domains,
        "users": users,
        "blogs": blogs,
        "resources": resources,
        "thank_you": thank_you
    }

    return render_template("analytics.html", analytics=analytics_data)

@analytics_bp.route("/analytics/<domain>")
def analytics_for_domain(domain):
    # Fetch data for the specific domain from the `domains` table
    conn = get_mysql_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT domain, users, blogs, resources, thank_you FROM domains WHERE domain = %s", (domain,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Domain not found"}), 404

    # Format the data for analytics
    analytics_data = {
        "domain": row[0],
        "users": row[1],
        "blogs": row[2],
        "resources": row[3],
        "thank_you": row[4]
    }

    return jsonify(analytics_data)

@analytics_bp.route("/api/analytics")
def analytics_api():
    # Fetch all domain data from the `domains` table
    conn = get_mysql_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT domain, users, blogs, resources, thank_you FROM domains")
    rows = cursor.fetchall()
    conn.close()

    domains = [row[0] for row in rows]
    users = [row[1] for row in rows]
    blogs = [row[2] for row in rows]
    resources = [row[3] for row in rows]
    thank_you = [row[4] for row in rows]

    analytics_data = {
        "domains": domains,
        "users": users,
        "blogs": blogs,
        "resources": resources,
        "thank_you": thank_you
    }
    return jsonify(analytics_data)

@analytics_bp.route("/google-analytics")
def serve_analytics_page():
    # Fetch all domain data from the `domains` table
    conn = get_mysql_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT domain, users, blogs, resources, thank_you FROM domains")
    rows = cursor.fetchall()
    conn.close()

    domains = [row[0] for row in rows]
    users = [row[1] for row in rows]
    blogs = [row[2] for row in rows]
    resources = [row[3] for row in rows]
    thank_you = [row[4] for row in rows]

    analytics_data = {
        "domains": domains,
        "users": users,
        "blogs": blogs,
        "resources": resources,
        "thank_you": thank_you
    }
    return render_template("google-analytics.html", analytics_data=analytics_data)
