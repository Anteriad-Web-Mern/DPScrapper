from flask import Flask, redirect, render_template, request, jsonify, url_for, flash
from flask_cors import CORS
import os
import sqlite3
import json
import plotly.graph_objects as go
import plotly.utils
from threading import Thread
import fetch_data
from domain_utils import load_domains, add_domain

app = Flask(__name__, template_folder="templates")

DB_MAIN = "wordpress_data.db"
DB_CREDENTIALS = "credentials.db"

# ---------------------- Utility Functions ----------------------

def execute_query(query, values=(), fetch=False):
    with sqlite3.connect(DB_CREDENTIALS) as conn:
        cursor = conn.cursor()
        cursor.execute(query, values)
        if fetch:
            return cursor.fetchall()
        conn.commit()

def get_data():
    conn = sqlite3.connect(DB_MAIN)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM domains")
    rows = cursor.fetchall()
    conn.close()
    return [{"domain": row[0], "users": row[1], "blogs": row[2],
             "resources": row[3], "thank_you": row[4]} for row in rows]

def get_all_tasks():
    try:
        rows = execute_query("SELECT id, task_name, domain, status FROM scraping_tasks", fetch=True)
        return [{"id": r[0], "task_name": r[1], "domain": r[2], "status": r[3]} for r in rows]
    except Exception:
        return []

# ---------------------- Routes ----------------------

@app.route("/")
def home():
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect(DB_MAIN)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM domains")
    domain_stats = cursor.fetchall()
    conn.close()
    return render_template("dashboard.html", domain_stats=domain_stats)

@app.route("/scrape-now")
def scrape_now():
    run_fetch()
    flash("✅ Scraping completed successfully!", "success")
    return redirect(url_for("dashboard"))

@app.route("/available-domains")
def get_domains():
    """Fetch all available domains."""
    domains = load_domains()
    return jsonify(domains=[d["domain"] for d in domains])

@app.route("/visualize")
def visualize():
    data = get_data()
    domains = [d["domain"] for d in data]
    users = [d["users"] for d in data]
    blogs = [d["blogs"] for d in data]
    resources = [d["resources"] for d in data]
    thank_you = [d["thank_you"] for d in data]

    graph_data = [
        {"data": [go.Bar(x=domains, y=users, name="Users")], "layout": go.Layout(title="Users")},
        {"data": [go.Bar(x=domains, y=blogs, name="Blogs")], "layout": go.Layout(title="Blogs")},
        {"data": [go.Bar(x=domains, y=thank_you, name="Thank-You Pages")], "layout": go.Layout(title="Thank-You Pages")},
    ]
    return render_template("visualize.html", graph_data=json.dumps(graph_data, cls=plotly.utils.PlotlyJSONEncoder))

@app.route("/fetch_data", methods=["POST"])
def fetch_data_route():
    Thread(target=fetch_data.run_fetch).start()
    return jsonify({"message": "Data fetching started! Refresh in a few seconds."})

@app.route("/add-task", methods=["POST"])
def add_task():
    data = request.json
    execute_query(
        "INSERT OR IGNORE INTO scraping_tasks (task_name, domain, status) VALUES (?, ?, ?)",
        (data["task_name"], data["domain"], "Pending")
    )
    return jsonify({"message": "Task added successfully."})

@app.route("/add-credentials", methods=["POST"])
def add_credentials():
    data = request.json
    execute_query(
        "INSERT OR REPLACE INTO credentials (domain, username, password) VALUES (?, ?, ?)",
        (data["domain"], data["username"], data["password"])
    )
    return jsonify({"message": "Credentials saved successfully."})

@app.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = get_all_tasks()
    return jsonify(tasks)

@app.route("/add-domain", methods=["POST"])
def add_domain_route():
    """Add a new domain."""
    data = request.json
    domain = data.get("domain")
    username = data.get("username", "")
    app_password = data.get("app_password", "")
    if not domain:
        return jsonify({"success": False, "message": "Domain is required."}), 400
    result = add_domain(domain, username, app_password)
    return jsonify(result)

@app.route("/results")
def results_summary():
    conn = sqlite3.connect(DB_MAIN)
    cursor = conn.cursor()

    # Fetch data for all domains
    cursor.execute("SELECT domain, users, blogs, resources, thank_you FROM domains")
    all_rows = cursor.fetchall()
    conn.close()

    # Calculate summary metrics
    total_users = sum(row[1] for row in all_rows)
    total_blogs = sum(row[2] for row in all_rows)
    total_resources = sum(row[3] for row in all_rows)
    total_thank_you = sum(row[4] for row in all_rows)

    summary_data = {
        "total_users": total_users,
        "total_blogs": total_blogs,
        "total_resources": total_resources,
        "total_thank_you": total_thank_you,
    }

    return render_template("results.html", all_results=all_rows, summary=summary_data)

@app.route("/results/<domain>")
def results_for_domain(domain):
    import sqlite3
    conn = sqlite3.connect(DB_MAIN)
    cursor = conn.cursor()
    cursor.execute("SELECT domain, users, blogs, resources, thank_you FROM domains WHERE domain = ?", (domain,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return render_template("results.html", result=None, error="Domain not found")

    result_data = {
        "domain": row[0],
        "users": row[1],
        "blogs": row[2],
        "resources": row[3],
        "thank_you": row[4]
    }
    analytics_data = {
        "labels": ["Users", "Blogs", "Resources", "Thank-You Pages"],
        "values": [row[1], row[2], row[3], row[4]]
    }
    return render_template("results.html", result=result_data, analytics=analytics_data)

@app.route("/analytics")
def analytics():
    # Fetch all domain data from the `domains` table
    conn = sqlite3.connect(DB_MAIN)
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

@app.route("/analytics/<domain>")
def analytics_for_domain(domain):
    # Fetch data for the specific domain from the `domains` table
    conn = sqlite3.connect(DB_MAIN)
    cursor = conn.cursor()
    cursor.execute("SELECT domain, users, blogs, resources, thank_you FROM domains WHERE domain = ?", (domain,))
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

# ---------------------- Scraping Tasks Page ----------------------

@app.route("/scraping-tasks")
def scraping_tasks():
    tasks = get_all_tasks()
    return render_template("scraping-tasks.html", tasks=tasks)

@app.route("/run-scraping", methods=["POST"])
def run_scraping():
    domain = request.json.get("domain")
    if not domain:
        return jsonify({"success": False, "message": "No domain specified"})
    # Simulate scraping logic
    print(f"Running scraping for domain: {domain}")
    return jsonify({"success": True})

@app.route("/task/<int:task_id>/stop", methods=["POST"])
def stop_task(task_id):
    execute_query("UPDATE scraping_tasks SET status = ? WHERE id = ?", ("Stopped", task_id))
    return jsonify({"message": "Task stopped successfully."})

@app.route("/task/<int:task_id>/view", methods=["GET"])
def view_task(task_id):
    task = execute_query("SELECT * FROM scraping_tasks WHERE id = ?", (task_id,), fetch=True)
    if task:
        return jsonify({
            "id": task[0][0],
            "task_name": task[0][1],
            "domain": task[0][2],
            "status": task[0][3]
        })
    return jsonify({"error": "Task not found"}), 404

# ---------------------- Main ----------------------

if __name__ == "__main__":
    Thread(target=fetch_data.run_fetch).start()
    app.run(debug=True)
