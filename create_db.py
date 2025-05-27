import sqlite3

DB_MAIN = "wordpress_data.db"
DB_CREDENTIALS = "credentials.db"

# Connect to the credentials database
conn_credentials = sqlite3.connect(DB_CREDENTIALS)
cursor_credentials = conn_credentials.cursor()

# Create the credentials table
cursor_credentials.execute('''
CREATE TABLE IF NOT EXISTS credentials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain TEXT UNIQUE,
    username TEXT,
    password TEXT
)
''')

# Create the scraping_tasks table
cursor_credentials.execute('''
CREATE TABLE IF NOT EXISTS scraping_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name TEXT,
    domain TEXT UNIQUE
)
''')

conn_credentials.commit()
conn_credentials.close()

# Connect to the main database
conn_main = sqlite3.connect(DB_MAIN)
cursor_main = conn_main.cursor()

# Create the `results` table
cursor_main.execute('''
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain TEXT NOT NULL,
        data_type TEXT NOT NULL,
        extracted_data TEXT NOT NULL
    )
''')

# Create the `domains` table if it doesn't already exist
cursor_main.execute('''
    CREATE TABLE IF NOT EXISTS domains (
        domain TEXT PRIMARY KEY,
        users INT,
        blogs INT,
        resources INT,
        thank_you INT
    )
''')

conn_main.commit()
conn_main.close()

print("✅ Database and tables created successfully!")
