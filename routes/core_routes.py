from flask import Blueprint, redirect, url_for, render_template, jsonify, request
from domain_utils import load_domains, add_domain
from utils.db import execute_query

core_bp = Blueprint('core', __name__)

@core_bp.route("/")
def home():
    return redirect(url_for("dashboard.dashboard"))

@core_bp.route("/available-domains")
def get_domains():
    domains = load_domains()
    return jsonify(domains=[d["domain"] for d in domains])

@core_bp.route("/add-credentials", methods=["POST"])
def add_credentials():
    data = request.json
    execute_query(
        "REPLACE INTO credentials (domain, username, password) VALUES (%s, %s, %s)",
        (data["domain"], data["username"], data["password"])
    )
    return jsonify({"message": "Credentials saved successfully."})

@core_bp.route("/add-domain", methods=["POST"])
def add_domain_route():
    data = request.json
    domain = data.get("domain")
    username = data.get("username", "")
    app_password = data.get("app_password", "")
    if not domain:
        return jsonify({"success": False, "message": "Domain is required."}), 400
    result = add_domain(domain, username, app_password)
    return jsonify(result)

@core_bp.route("/index")
def index():
    return render_template("index.html")

@core_bp.route("/kinsta")
def kinsta_page():
    return render_template("kinsta.html")
