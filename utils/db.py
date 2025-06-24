import mysql.connector
from config import MYSQL_CONFIG

def get_mysql_conn():
    return mysql.connector.connect(**MYSQL_CONFIG)

def execute_query(query, values=(), fetch=False):
    with get_mysql_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(query, values)
        if fetch:
            return cursor.fetchall()
        conn.commit()

def get_data():
    conn = get_mysql_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM domains")
    rows = cursor.fetchall()
    conn.close()
    return [{"domain": row[0], "users": row[1], "blogs": row[2],
             "resources": row[3], "thank_you": row[4]} for row in rows]

def get_all_tasks():
    return [
        {"id": r[0], "task_name": r[1], "domain": r[2], "status": r[3]}
        for r in execute_query("SELECT id, task_name, domain, status FROM scraping_tasks", fetch=True)
    ]
