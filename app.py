from flask import Flask, redirect, render_template, request, jsonify, url_for, flash
from flask_cors import CORS
from flask_mail import Mail, Message
import os
import mysql.connector
import json
import plotly.graph_objects as go
import plotly.utils
from threading import Thread
import fetch_data
from domain_utils import load_domains, add_domain
import requests
from requests.auth import HTTPBasicAuth
import analytics_report  # Import the analytics_report.py file
import subprocess
import time  # Import the time module
import logging

app = Flask(__name__, template_folder="templates")
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# MySQL connection config
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'hritik1234',
    'database': 'wordpress_data',
}

KINSTA_BASE_URL = "https://api.kinsta.com/v2"

def get_kinsta_headers(api_key):
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

# Load domains configuration from JSON file
try:
    with open("domain_config.json", "r") as f:
        DOMAINS_CONFIG = json.load(f)
except FileNotFoundError:
    print("Error: domain_config.json not found. Please create this file.")
    DOMAINS_CONFIG = []  # Initialize to an empty list to prevent further errors

def get_mysql_conn():
    return mysql.connector.connect(**MYSQL_CONFIG)

# ---------------------- Utility Functions ----------------------

def execute_query(query, values=(), fetch=False):
    with get_mysql_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(query, values)
        if fetch:
            return cursor.fetchall()
        conn.commit()

def get_data():
    conn = get_mysql_conn()
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

# ---------------------- Scrapy Trigger ----------------------
def run_scrapy_spider(domain_config):
    try:
        api_key = domain_config["api_key"]
        site_id = domain_config["site_id"]
        domain = domain_config["domain"]

        scrapy_command = [
            "/mnt/c/Users/hrsharma/Desktop/WebSrapper/DPScrapper/venv/bin/scrapy", "crawl", "kinsta",
            "-a", f"kinsta_api_key={api_key}",
            "-a", f"site_id={site_id}",
            "-o", f"output_{domain}.json"
        ]
        subprocess.run(scrapy_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Scrapy error: {e}")

# ---------------------- Kinsta API Routes ----------------------

@app.route("/clear-cache/<string:domain>", methods=["POST"])
def clear_site_cache(domain):
    domain_config = next((d for d in DOMAINS_CONFIG if d["domain"] == domain), None)
    if not domain_config:
        return jsonify({"error": "Domain config not found"}), 404

    site_id = domain_config.get('site_id')
    environment_id = domain_config.get('environment_id')
    api_key = domain_config.get('api_key')

    if not site_id:
        return jsonify({"error": "Site ID not found in domain config"}), 400

    if not environment_id:
        return jsonify({"error": "Environment ID not found in domain config"}), 400

    url = f"{KINSTA_BASE_URL}/sites/tools/clear-cache"
    headers = get_kinsta_headers(api_key)

    payload = {
        "environment_id": environment_id
    }

    try:
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 202:
            # Cache clearing is in progress
            operation_id = response.json().get("operation_id")
            if operation_id:
                # Poll the operation status until it's completed
                status = poll_operation_status(api_key, operation_id)
                return jsonify({"message": status})
            else:
                return jsonify({"error": "Cache clearing in progress, but operation_id not found", "response": response.text}), 500
        else:
            return jsonify({"error": "Failed to clear cache", "response": response.text}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 500

def poll_operation_status(api_key, operation_id, timeout=60, interval=5):
    """
    Polls the status of a Kinsta API operation until it's completed or a timeout is reached.
    """
    start_time = time.time()
    headers = get_kinsta_headers(api_key)
    while True:
        # Check if the timeout has been reached
        if time.time() - start_time > timeout:
            return "Cache clearing timed out."

        # Poll the operation status
        url = f"{KINSTA_BASE_URL}/operations/{operation_id}"
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            operation_data = response.json()
            status = operation_data.get("status")

            if status == "complete":
                return "Cache cleared successfully"
            elif status == "failed":
                return f"Cache clearing failed: {operation_data.get('error', 'Unknown error')}"
            else:
                print(f"Cache clearing status: {status}.  Checking again in {interval} seconds...")
                time.sleep(interval)  # Wait before polling again
        except requests.exceptions.RequestException as e:
            return f"Error checking cache clearing status: {str(e)}"
        except json.JSONDecodeError:
            return "Error decoding JSON response when checking cache clearing status."

@app.route("/plugins/<string:domain>", methods=["GET"])
def get_site_plugins(domain):
    logger.info(f"Attempting to fetch plugins for domain: {domain}")
    domain_config = next((d for d in DOMAINS_CONFIG if d["domain"] == domain), None)
    if not domain_config:
        logger.warning(f"Domain config not found for domain: {domain}")
        return jsonify({"error": "Domain config not found"}), 404

    environment_id = domain_config.get('environment_id')
    api_key = domain_config.get('api_key')  # Get the API key
    if not environment_id:
        logger.error(f"Environment ID not found in domain config for domain: {domain}")
        return jsonify({"error": "Environment ID not found in domain config"}), 400

    url = f"{KINSTA_BASE_URL}/sites/environments/{environment_id}/plugins"
    try:
        logger.info(f"Attempting to fetch plugins from: {url}")
        response = requests.get(url, headers=get_kinsta_headers(api_key))

        if response.status_code == 200:
            logger.info(f"Successfully fetched plugins from: {url}")
            plugins_data = response.json()
            if "environment" in plugins_data and "container_info" in plugins_data["environment"] and "wp_plugins" in plugins_data["environment"]["container_info"]:
                return jsonify(plugins_data["environment"]["container_info"]["wp_plugins"]["data"])
            else:
                logger.warning("Unexpected JSON structure in Kinsta API response")
                return jsonify({"error": "Unexpected JSON structure in Kinsta API response"}), 500
        else:
            logger.error(f"Failed to fetch plugins. Status code: {response.status_code}, Response: {response.text}")
            return jsonify({"error": "Failed to fetch plugins", "response": response.text}), response.status_code
    except requests.exceptions.RequestException as e:
        logger.exception(f"Request failed: {str(e)}")
        return jsonify({"error": f"Request failed: {str(e)}"}), 500

@app.route("/themes/<string:domain>", methods=["GET"])
def get_site_themes(domain):
    logger.info(f"Attempting to fetch themes for domain: {domain}")
    domain_config = next((d for d in DOMAINS_CONFIG if d["domain"] == domain), None)
    if not domain_config:
        logger.warning(f"Domain config not found for domain: {domain}")
        return jsonify({"error": "Domain config not found"}), 404

    environment_id = domain_config.get('environment_id')
    api_key = domain_config.get('api_key')  # Get the API key
    if not environment_id:
        logger.error(f"Environment ID not found in domain config for domain: {domain}")
        return jsonify({"error": "Environment ID not found in domain config"}), 400

    url = f"{KINSTA_BASE_URL}/sites/environments/{environment_id}/themes"
    try:
        logger.info(f"Attempting to fetch themes from: {url}")
        response = requests.get(url, headers=get_kinsta_headers(api_key))

        if response.status_code == 200:
            logger.info(f"Successfully fetched themes from: {url}")
            themes_data = response.json()
            if "environment" in themes_data and "container_info" in themes_data["environment"] and "wp_themes" in themes_data["environment"]["container_info"]:
                 return jsonify(themes_data["environment"]["container_info"]["wp_themes"]["data"])
            else:
                logger.warning("Unexpected JSON structure in Kinsta API response")
                return jsonify({"error": "Unexpected JSON structure in Kinsta API response"}), 500
        else:
            logger.error(f"Failed to fetch themes. Status code: {response.status_code}, Response: {response.text}")
            return jsonify({"error": "Failed to fetch themes", "response": response.text}), response.status_code
    except requests.exceptions.RequestException as e:
        logger.exception(f"Request failed: {str(e)}")
        return jsonify({"error": f"Request failed: {str(e)}"}), 500

# ---------------------- Routes ----------------------

@app.route("/")
def home():
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
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
    # Prepare data for visualization
    domains = [row[0] for row in domain_stats]
    users = [row[1] for row in domain_stats]
    blogs = [row[2] for row in domain_stats]
    resources = [row[3] for row in domain_stats]
    thank_you = [row[4] for row in domain_stats]

    analytics = {
        "domains": domains,
        "users": users,
        "blogs": blogs,
        "resources": resources,
        "thank_you": thank_you
    }

    return render_template("dashboard.html", domain_stats=domain_stats, summary=summary, analytics=analytics)

@app.route("/scrape-now")
def scrape_now():
    Thread(target=fetch_data.run_fetch).start()
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
        "INSERT IGNORE INTO scraping_tasks (task_name, domain, status) VALUES (%s, %s, %s)",
        (data["task_name"], data["domain"], "Pending")
    )
    return jsonify({"message": "Task added successfully."})

@app.route("/add-credentials", methods=["POST"])
def add_credentials():
    data = request.json
    execute_query(
        "REPLACE INTO credentials (domain, username, password) VALUES (%s, %s, %s)",
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
    conn = get_mysql_conn()
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
    conn = get_mysql_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT domain, users, blogs, resources, thank_you FROM domains WHERE domain = %s", (domain,))
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

    # Fetch Google Analytics data
    analytics_data = analytics_report.report  # Assuming analytics_report.report contains the data

    return render_template("results.html", result=result_data, analytics_data=analytics_data)

@app.route("/analytics")
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

@app.route("/analytics/<domain>")
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

# Flask-Mail config (update with your SMTP server details)
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'your_email@example.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

@app.route('/bulk-add-user', methods=['GET', 'POST'])
def bulk_add_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'subscriber')

        with open('domains.json') as f:
            domains = json.load(f)
        results = []
        registered = False
        for domain in domains:
            url = domain['url'].rstrip('/') + '/wp-json/wp/v2/users'
            auth = HTTPBasicAuth(domain['username'], domain['password'])
            data = {
                'username': username,
                'email': email,
                'password': password,
                'role': role
            }

            try:
                resp = requests.post(url, auth=auth, json=data, timeout=10)
                if resp.status_code in (200, 201):
                    results.append((domain['domain'], '✅ Success'))
                    registered = True
                else:
                    try:
                        error_msg = resp.json().get('message', 'Unknown error')
                    except:
                        error_msg = resp.text
                    results.append((domain['domain'], f"❌ Failed: {resp.status_code} - {error_msg}"))
            except Exception as e:
                results.append((domain['domain'], f"🚨 Error: {e}"))

        # Send email if registered on at least one domain
        if registered:
            msg = Message(
                subject="Welcome to Our Platform",
                sender=app.config['MAIL_USERNAME'],
                recipients=[email],
                body=f"Hello {username},\n\nYour account has been created on our platform. You can now log in.\n\nThanks!"
            )
            mail.send(msg)

        return render_template('bulk_add_user.html', results=results)

    return render_template('bulk_add_user.html', results=None)



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
    execute_query("UPDATE scraping_tasks SET status = %s WHERE id = %s", ("Stopped", task_id))
    return jsonify({"message": "Task stopped successfully."})

@app.route("/task/<int:task_id>/view", methods=["GET"])
def view_task(task_id):
    task = execute_query("SELECT * FROM scraping_tasks WHERE id = %s", (task_id,), fetch=True)
    if task:
        return jsonify({
            "id": task[0][0],
            "task_name": task[0][1],
            "domain": task[0][2],
            "status": task[0][3]
        })
    return jsonify({"error": "Task not found"}), 404

@app.route('/api/users')
def api_users():
    role = request.args.get('role')
    # Use the first domain as the source of truth for users
    with open('domains.json') as f:
        domains = json.load(f)
    domain = domains[0]
    url = domain['url'].rstrip('/') + '/wp-json/wp/v2/users'
    auth = HTTPBasicAuth(domain['username'], domain['password'])
    params = {'per_page': 100}
    if role:
        params['roles'] = role
    resp = requests.get(url, auth=auth, params=params)
    if resp.status_code == 200:
        return jsonify([
            {
                'id': u['id'],
                'name': u['name'],
                'email': u.get('email', ''),
                'roles': u.get('roles', [])
            } for u in resp.json()
        ])
    return jsonify([]), resp.status_code

@app.route('/api/add-user', methods=['POST'])
def api_add_user():
    data = request.json
    # Add user to all domains
    with open('domains.json') as f:
        domains = json.load(f)
    success = False
    errors = []  # Collect errors from each domain
    for domain in domains:
        url = domain['url'].rstrip('/') + '/wp-json/wp/v2/users'
        auth = HTTPBasicAuth(domain['username'], domain['password'])
        try:
            resp = requests.post(url, auth=auth, json=data)
            resp.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            if resp.status_code in (200, 201):
                success = True
            else:
                errors.append(f"Domain: {domain['domain']}, Status Code: {resp.status_code}, Response: {resp.text}")
        except requests.exceptions.RequestException as e:
            errors.append(f"Domain: {domain['domain']}, Error: {str(e)}")

    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'errors': errors}), 400

@app.route('/user-management')
def user_management():
    return render_template('user-management.html')

# ----------------------Google Analytics API ----------------------

# Run analytics_report.py to get the report data
report = analytics_report.report

@app.route("/api/analytics")
def analytics_api():
    return jsonify(report)

@app.route("/google-analytics")
def serve_analytics_page():
    return render_template("google-analytics.html", analytics_data=report)  # Pass the data to the template

# API endpoint to trigger the scraping for all domains
@app.route('/scrape', methods=['POST'])
def scrape():
    all_results = {}
    for domain_config in DOMAINS_CONFIG:
        domain = domain_config["domain"]
        results = run_scrapy_spider(domain_config)
        all_results[domain] = results  # Store results by domain

    return jsonify(all_results)

# Serve the frontend
@app.route('/')
def index():
    return render_template('index.html')

@app.route("/kinsta")
def kinsta():
    return render_template("kinsta.html")

# ---------------------- Main ----------------------

if __name__ == "__main__":
    Thread(target=fetch_data.run_fetch).start()
    app.run(host='0.0.0.0', port=5000, debug=True)
