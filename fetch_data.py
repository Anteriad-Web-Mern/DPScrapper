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
conn = sqlite3.connect(DB_MAIN, check_same_thread=False)
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


def fetch_all_items(base_url, auth):
    items = []
    page = 1
    last_page_items = None

    while True:
        time.sleep(1)
        try:
            params = { 'per_page': 100, 'page': page }
            response = requests.get(base_url, auth=auth, params=params, timeout=10)
            print(f"Fetching {response.url}, Status: {response.status_code}")

            if response.status_code in [400, 401, 404]:
                break

            page_items = response.json()
            if not isinstance(page_items, list):
                break

            items.extend(page_items)
            # stop if fewer results than per_page or page repeats
            if len(page_items) < 100 or page_items == last_page_items:
                break

            last_page_items = page_items
            page += 1
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching {base_url}: {e}")
            break
    return items


def fetch_users_once(url, auth):
    try:
        response = requests.get(url, auth=auth, timeout=10)
        print(f"Fetching {url}, Status: {response.status_code}")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"❌ Error fetching users: {e}")
        return []


def fetch_and_store(domain_info):
    domain = domain_info["domain"]
    base_url = domain_info["url"].rstrip('/')
    username = domain_info.get("username", "")
    password = domain_info.get("password", "")
    auth = HTTPBasicAuth(username, password)

    try:
        # Fetch data via clean URLs plus params
        users = fetch_users_once(f"{base_url}/wp-json/custom/v1/users", auth)
        blogs = fetch_all_items(f"{base_url}/wp-json/wp/v2/posts", auth)
        pages = fetch_all_items(f"{base_url}/wp-json/wp/v2/pages", auth)

        thank_you_pages = sum(
            1 for p in pages
            if isinstance(p, dict) and 'slug' in p and 'thank-you' in p['slug'].lower()
        )

        with conn:
            cursor.execute(
                '''
                    REPLACE INTO domains (domain, users, blogs, resources, thank_you)
                    VALUES (?, ?, ?, ?, ?)
                ''',
                (domain, len(users), len(blogs), len(pages), thank_you_pages)
            )
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
        t = threading.Thread(target=fetch_and_store, args=(domain_info,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
    print("✅ Data fetching completed!")


if __name__ == '__main__':
    
    run_fetch()
