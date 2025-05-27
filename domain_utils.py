import json
import os

DOMAINS_FILE = "domains.json"

def load_domains():
    """Load domains from the JSON file."""
    if not os.path.exists(DOMAINS_FILE):
        return []
    with open(DOMAINS_FILE, "r") as file:
        return json.load(file)

def save_domains(domains):
    """Save domains to the JSON file."""
    with open(DOMAINS_FILE, "w") as file:
        json.dump(domains, file, indent=4)

def add_domain(domain, username="", app_password=""):
    """Add a new domain to the JSON file."""
    domains = load_domains()
    if any(d["domain"] == domain for d in domains):
        return {"success": False, "message": "Domain already exists."}
    domains.append({"domain": domain, "username": username, "app_password": app_password})
    save_domains(domains)
    return {"success": True, "message": "Domain added successfully."}