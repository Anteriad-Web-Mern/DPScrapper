import requests
from requests.auth import HTTPBasicAuth
import mysql.connector
import threading
import time
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MySQL connection config (read from environment variables)
MYSQL_CONFIG = {
    'host': os.environ.get('MYSQL_HOST'),
    'user': os.environ.get('MYSQL_USER'),
    'password': os.environ.get('MYSQL_PASSWORD'),
    'database': os.environ.get('MYSQL_DATABASE'),
}

# Path to the JSON file
DOMAINS_FILE = "domains.json"


def get_mysql_conn():
    return mysql.connector.connect(**MYSQL_CONFIG)


# Ensure the domains table exists
def ensure_domains_table():
    conn = get_mysql_conn()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS domains (
            domain VARCHAR(255) PRIMARY KEY,
            users INT,
            blogs INT,
            resources INT,
            thank_you INT
        )
    ''')
    conn.commit()
    conn.close()


def load_domains_from_json():
    """Loads domains from the domains.json file."""
    try:
        with open(DOMAINS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {DOMAINS_FILE} not found.")
        return []  # Return an empty list if the file is not found
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {DOMAINS_FILE}: {e}")
        return []  # Return an empty list if there's a JSON decoding error


def fetch_data_for_domain(domain_data):
    """Fetches data for a single domain."""
    domain = domain_data['domain']  # Extract the domain name
    try:
        # Fetch users
        users_url = f"https://{domain}/wp-json/wp/v2/users"
        users_response = requests.get(users_url)
        users_count = len(users_response.json()) if users_response.status_code == 200 else 0

        # Fetch blogs
        blogs_url = f"https://{domain}/wp-json/wp/v2/posts"
        blogs_response = requests.get(blogs_url)
        blogs_count = len(blogs_response.json()) if blogs_response.status_code == 200 else 0

        # Fetch resources
        resources_url = f"https://{domain}/wp-json/wp/v2/media"
        resources_response = requests.get(resources_url)
        resources_count = len(resources_response.json()) if resources_response.status_code == 200 else 0

        # Thank you pages
        thank_you_url = f"https://{domain}/wp-json/wp/v2/pages?search=thank%20you"
        thank_you_response = requests.get(thank_you_url)
        thank_you_count = len(thank_you_response.json()) if thank_you_response.status_code == 200 else 0

        return {
            'domain': domain,
            'users': users_count,
            'blogs': blogs_count,
            'resources': resources_count,
            'thank_you': thank_you_count
        }
    except Exception as e:
        print(f"Error fetching data for {domain}: {e}")
        return None


def store_data_in_mysql(data):
    """Stores the fetched data in the MySQL database."""
    if data is None:
        print("Skipping storage due to None data.")
        return
    try:
        conn = get_mysql_conn()
        cursor = conn.cursor()

        query = """
            INSERT INTO domains (domain, users, blogs, resources, thank_you)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                users = %s,
                blogs = %s,
                resources = %s,
                thank_you = %s
        """
        values = (
            data['domain'], data['users'], data['blogs'], data['resources'], data['thank_you'],
            data['users'], data['blogs'], data['resources'], data['thank_you']
        )
        cursor.execute(query, values)
        conn.commit()
        print(f"Data stored for {data['domain']}")
    except Exception as e:
        print(f"Error storing data in MySQL: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()


def run_fetch():
    """Main function to run the data fetching and storing process."""
    domains = load_domains_from_json()
    if not domains:
        print("No domains to fetch data for.")
        return

    threads = []
    for domain_data in domains:
        thread = threading.Thread(target=lambda d=domain_data: store_data_in_mysql(fetch_data_for_domain(d)))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("Data fetching and storing complete.")


if __name__ == "__main__":
    run_fetch()
