from flask import Blueprint, jsonify, request
from config import get_kinsta_headers, KINSTA_BASE_URL
import json, requests, time, logging, os

kinsta_bp = Blueprint('kinsta', __name__)
logger = logging.getLogger(__name__)

KINSTA_DIR = os.path.dirname(os.path.abspath(__file__))
DOMAIN_CONFIG_PATH = os.path.join(KINSTA_DIR, '..', 'domain_config.json')

try:
    with open(DOMAIN_CONFIG_PATH, "r") as f:
        DOMAINS_CONFIG = json.load(f)
except FileNotFoundError:
    print(f"Error: {DOMAIN_CONFIG_PATH} not found. Please create this file.")
    DOMAINS_CONFIG = []



# ---------------------- Kinsta API Routes ----------------------


@kinsta_bp.route("/clear-cache/<string:domain>", methods=["POST"])
def clear_site_cache(domain):
    domain_config = next((d for d in DOMAINS_CONFIG if d["domain"] == domain), None)
    if not domain_config:
        return jsonify({"error": "Domain config not found"}), 404

    site_id = domain_config.get('site_id')
    environment_id = domain_config.get('environment_id')
    api_key = domain_config.get('api_key')

    if not site_id or not environment_id:
        return jsonify({"error": "Site ID or Environment ID missing"}), 400

    url = f"{KINSTA_BASE_URL}/sites/tools/clear-cache"
    headers = get_kinsta_headers(api_key)
    payload = { "environment_id": environment_id }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 202:
            operation_id = response.json().get("operation_id")
            if operation_id:
                status = poll_operation_status(api_key, operation_id)
                return jsonify({"message": status})
            return jsonify({"error": "operation_id missing"}), 500
        return jsonify({"error": "Failed to clear cache", "response": response.text}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 500

def poll_operation_status(api_key, operation_id, timeout=60, interval=2):
    start_time = time.time()
    headers = get_kinsta_headers(api_key)
    while True:
        if time.time() - start_time > timeout:
            return "Cache clearing timed out."
        url = f"{KINSTA_BASE_URL}/operations/{operation_id}"
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            status = response.json().get("status")
            if status == "complete":
                return "Cache cleared successfully"
            if status == "failed":
                return f"Cache clearing failed: {response.json().get('error', 'Unknown error')}"
            time.sleep(interval)
        except requests.exceptions.RequestException as e:
            return f"Error checking status: {str(e)}"

# Similarly define get_site_plugins, get_site_themes
@kinsta_bp.route("/plugins/<string:domain>", methods=["GET"])
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

@kinsta_bp.route("/themes/<string:domain>", methods=["GET"])
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