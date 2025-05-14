import requests
from requests.auth import HTTPBasicAuth
import sqlite3
import threading
import time
import json
import os


DB_MAIN = "wordpress_data.db"
# Path to the JSON file
DOMAINS_FILE = "domains.json"

# DB Setup
conn = sqlite3.connect("wordpress_data.db", check_same_thread=False)
cursor = conn.cursor()

# Drop and recreate the table to ensure all columns exist
cursor.execute("DROP TABLE IF EXISTS domains")
cursor.execute('''
    CREATE TABLE IF NOT EXISTS domains (
        domain TEXT PRIMARY KEY,
        users INT,
        blogs INT,
        resources INT,
        thank_you INT
    )
''')
conn.commit()

def load_domains_from_json():
    if not os.path.exists(DOMAINS_FILE):
        print(f"❌ JSON file '{DOMAINS_FILE}' not found.")
        return []
    with open(DOMAINS_FILE, "r") as file:
        return json.load(file)

def fetch_all_items(url, auth):
    items = []
    page = 1
    while True:
        time.sleep(1)
        try:
            url = url.rstrip("/")
            separator = '&' if '?' in url else '?'
            full_url = f"{url}{separator}page={page}"
            response = requests.get(full_url, auth=auth, timeout=10)
            print(f"Fetching {full_url}, Status: {response.status_code}")
            if response.status_code in [400, 401]:
                break
            page_items = response.json()
            if not page_items:
                break
            items.extend(page_items)
            page += 1
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching {url}: {e}")
            break
    return items

def save_results_to_db(domain, data_type, extracted_data):
    """Save scraped results to the database."""
    conn = sqlite3.connect(DB_MAIN)
    cursor = conn.cursor()

    # Insert the scraped data into the `results` table
    cursor.execute('''
        INSERT INTO results (domain, data_type, extracted_data)
        VALUES (?, ?, ?)
    ''', (domain, data_type, extracted_data))

    conn.commit()
    conn.close()
    print(f"✅ Data saved for domain: {domain}, type: {data_type}")

def fetch_and_store(domain_info):
    domain = domain_info["domain"]
    url = domain_info["url"].rstrip("/")
    username = domain_info["username"]
    password = domain_info["password"]
    auth = HTTPBasicAuth(username, password)

    try:
        blogs = fetch_all_items(f"{url}/wp-json/wp/v2/posts?per_page=100", auth)
        resources = fetch_all_items(f"{url}/wp-json/wp/v2/pages?per_page=100", auth)
        pages = fetch_all_items(f"{url}/wp-json/wp/v2/pages?per_page=100", auth)
        thank_you_pages = sum(1 for page in pages if "thank-you" in page.get("slug", "").lower())

        with conn:
            cursor.execute('''
                REPLACE INTO domains (domain, users, blogs, resources, thank_you)
                VALUES (?, ?, ?, ?, ?)
            ''', (domain, 0, len(blogs), len(resources), thank_you_pages))
        print(f"✅ Data stored for {domain}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching {domain}: {e}")
    except sqlite3.Error as e:
        print(f"❌ Database error for {domain}: {e}")

def run_fetch():
    domains = load_domains_from_json()
    if not domains:
        print("❌ No domains to scrape.")
        return

    threads = []
    for domain_info in domains:
        thread = threading.Thread(target=fetch_and_store, args=(domain_info,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
    print("✅ Data fetching completed!")
