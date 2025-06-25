from flask import Blueprint, redirect, url_for, render_template, jsonify, request
from domain_utils import load_domains, add_domain
from utils.db import execute_query
import os
import json

core_bp = Blueprint('core', __name__)

@core_bp.route("/")
def home():
    return redirect(url_for("dashboard.dashboard"))

@core_bp.route("/available-domains")
def get_domains():
    domains = load_domains()
    normalized = []
    for d in domains:
        domain_val = d.get("domain") or d.get("url")
        if not domain_val:
            continue
        normalized.append({
            "domain": domain_val,
            "status": d.get("status", "Active"),
            "category": d.get("category", ""),
            "hosted_on": d.get("hosted_on", ""),
            "group": d.get("group", d.get("category", "")),
        })
    return jsonify(normalized)

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

@core_bp.route("/add-dp", methods=["POST"])
def add_dp():
    data = request.get_json()
    domain_entry = {
        "domain": data.get("domain"),
        "name": data.get("name"),
        "username": data.get("username"),
        "password": data.get("password"),
        "category": data.get("category"),
        "hosted_on": data.get("hosted_on"),
        "status": data.get("status")
    }
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'domains.json'))
    try:
        with open(config_path, "r") as f:
            domains = json.load(f)
    except Exception:
        domains = []
    domains.append(domain_entry)
    with open(config_path, "w") as f:
        json.dump(domains, f, indent=2)
    return jsonify({"success": True})

@core_bp.route("/delete-dp", methods=["POST"])
def delete_dp():
    data = request.get_json()
    domain_to_delete = data.get("domain")
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'domains.json'))
    try:
        with open(config_path, "r") as f:
            domains = json.load(f)
        # Remove the domain with matching "domain" field
        domains = [d for d in domains if d.get("domain") != domain_to_delete]
        with open(config_path, "w") as f:
            json.dump(domains, f, indent=2)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
