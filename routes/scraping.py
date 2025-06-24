from flask import Blueprint, request, jsonify, render_template
from utils.db import get_mysql_conn, get_all_tasks, execute_query
import subprocess

scraping_bp = Blueprint('scraping', __name__)

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


@scraping_bp.route("/scraping-tasks")
def scraping_tasks():
    tasks = get_all_tasks()
    return render_template("scraping-tasks.html", tasks=tasks)

@scraping_bp.route("/run-scraping", methods=["POST"])
def run_scraping():
    domain = request.json.get("domain")
    if not domain:
        return jsonify({"success": False, "message": "No domain specified"})
    # Simulate scraping logic
    print(f"Running scraping for domain: {domain}")
    return jsonify({"success": True})

@scraping_bp.route("/task/<int:task_id>/stop", methods=["POST"])
def stop_task(task_id):
    execute_query("UPDATE scraping_tasks SET status = %s WHERE id = %s", ("Stopped", task_id))
    return jsonify({"message": "Task stopped successfully."})

@scraping_bp.route("/task/<int:task_id>/view", methods=["GET"])
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

# API endpoint to trigger the scraping for all domains
@scraping_bp.route('/scrape', methods=['POST'])
def scrape():
    all_results = {}
    for domain_config in DOMAINS_CONFIG:
        domain = domain_config["domain"]
        results = run_scrapy_spider(domain_config)
        all_results[domain] = results  # Store results by domain

    return jsonify(all_results)

@scraping_bp.route("/scrape-now")
def scrape_now():
    Thread(target=fetch_data.run_fetch).start()
    flash("✅ Scraping completed successfully!", "success")
    return redirect(url_for("dashboard"))