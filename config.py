import os

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
