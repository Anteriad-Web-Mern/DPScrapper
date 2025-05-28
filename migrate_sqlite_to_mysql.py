import sqlite3
import mysql.connector

# SQLite DB paths
DB_MAIN = "wordpress_data.db"
DB_CREDENTIALS = "credentials.db"

# MySQL connection config
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'hritik1234',
    'database': 'wordpress_data',
}

# Connect to MySQL
mysql_conn = mysql.connector.connect(**MYSQL_CONFIG)
mysql_cursor = mysql_conn.cursor()

# --- Create tables in MySQL ---
mysql_cursor.execute('''
CREATE TABLE IF NOT EXISTS credentials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    domain VARCHAR(255) UNIQUE,
    username VARCHAR(255),
    password VARCHAR(255)
)
''')

mysql_cursor.execute('''
CREATE TABLE IF NOT EXISTS scraping_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_name VARCHAR(255),
    domain VARCHAR(255) UNIQUE
)
''')

mysql_cursor.execute('''
CREATE TABLE IF NOT EXISTS results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    domain VARCHAR(255) NOT NULL,
    data_type VARCHAR(255) NOT NULL,
    extracted_data TEXT NOT NULL
)
''')

mysql_cursor.execute('''
CREATE TABLE IF NOT EXISTS domains (
    domain VARCHAR(255) PRIMARY KEY,
    users INT,
    blogs INT,
    resources INT,
    thank_you INT
)
''')

# --- Migrate credentials.db ---
sqlite_conn = sqlite3.connect(DB_CREDENTIALS)
sqlite_cursor = sqlite_conn.cursor()

sqlite_cursor.execute("SELECT * FROM credentials")
for row in sqlite_cursor.fetchall():
    mysql_cursor.execute(
        "INSERT IGNORE INTO credentials (id, domain, username, password) VALUES (%s, %s, %s, %s)",
        row
    )

sqlite_cursor.execute("SELECT * FROM scraping_tasks")
for row in sqlite_cursor.fetchall():
    mysql_cursor.execute(
        "INSERT IGNORE INTO scraping_tasks (id, task_name, domain) VALUES (%s, %s, %s)",
        row
    )

sqlite_conn.close()

# --- Migrate wordpress_data.db ---
sqlite_conn = sqlite3.connect(DB_MAIN)
sqlite_cursor = sqlite_conn.cursor()

sqlite_cursor.execute("SELECT * FROM results")
for row in sqlite_cursor.fetchall():
    mysql_cursor.execute(
        "INSERT IGNORE INTO results (id, domain, data_type, extracted_data) VALUES (%s, %s, %s, %s)",
        row
    )

sqlite_cursor.execute("SELECT * FROM domains")
for row in sqlite_cursor.fetchall():
    mysql_cursor.execute(
        "INSERT IGNORE INTO domains (domain, users, blogs, resources, thank_you) VALUES (%s, %s, %s, %s, %s)",
        row
    )

sqlite_conn.close()

mysql_conn.commit()
mysql_conn.close()

print("✅ Data migrated from SQLite to MySQL successfully!")