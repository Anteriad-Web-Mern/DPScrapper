

# API.md file

List of API's Used or Created across the site

## 🚀 API Documentation

Below are the main API endpoints available in this project.
All endpoints are relative to your server root (e.g., `http://localhost:5000/`).

---

### **Kinsta API Routes**

#### `POST /clear-cache/<domain>`

- **Description:** Clears the cache for a given domain using the Kinsta API.
- **URL Parameter:**
    - `domain` (string): The domain to clear cache for.
- **Response:**
    - `{ "message": "Cache cleared successfully" }`
    - Or error message.


#### `GET /plugins/<domain>`

- **Description:** Fetches the list of installed plugins for a given domain from Kinsta.
- **URL Parameter:**
    - `domain` (string): The domain to fetch plugins for.
- **Response:**
    - Array of plugin objects or error message.


#### `GET /themes/<domain>`

- **Description:** Fetches the list of installed themes for a given domain from Kinsta.
- **URL Parameter:**
    - `domain` (string): The domain to fetch themes for.
- **Response:**
    - Array of theme objects or error message.

---

### **Core Application Routes**

#### `GET /`

- **Description:** Redirects to the dashboard.


#### `GET /dashboard`

- **Description:** Renders the dashboard page with domain statistics and analytics.


#### `GET /scrape-now`

- **Description:** Triggers the scraping process in the background and redirects to the dashboard.


#### `GET /available-domains`

- **Description:** Returns a list of all available domains.
- **Response:**
    - `{ "domains": ["domain1.com", "domain2.com", ...] }`


#### `GET /visualize`

- **Description:** Renders a visualization page with analytics graphs.


#### `POST /fetch_data`

- **Description:** Starts the data fetching process in the background.
- **Response:**
    - `{ "message": "Data fetching started! Refresh in a few seconds." }`


#### `POST /add-task`

- **Description:** Adds a new scraping task.
- **Request Body:**

```json
{
  "task_name": "Task Name",
  "domain": "example.com"
}
```

- **Response:**
    - `{ "message": "Task added successfully." }`


#### `POST /add-credentials`

- **Description:** Saves or updates credentials for a domain.
- **Request Body:**

```json
{
  "domain": "example.com",
  "username": "user",
  "password": "pass"
}
```

- **Response:**
    - `{ "message": "Credentials saved successfully." }`


#### `GET /tasks`

- **Description:** Returns a list of all scraping tasks.
- **Response:**
    - Array of task objects.


#### `POST /add-domain`

- **Description:** Adds a new domain to the system.
- **Request Body:**

```json
{
  "domain": "example.com",
  "username": "user",
  "app_password": "app_pass"
}
```

- **Response:**
    - `{ "success": true, ... }` or error message.


#### `GET /results`

- **Description:** Renders a summary page with results for all domains.


#### `GET /results/<domain>`

- **Description:** Renders a results page for a specific domain, including analytics.


#### `GET /analytics`

- **Description:** Fetches analytics data for all domains.

---

### **Example Usage**

**Clear Cache**

```bash
curl -X POST http://localhost:5000/clear-cache/example.com
```

**Add Task**

```bash
curl -X POST http://localhost:5000/add-task \
     -H "Content-Type: application/json" \
     -d '{"task_name":"Scrape Example","domain":"example.com"}'
```


---

### **Notes**

- Some endpoints require specific domain configuration in `domain_config.json`.
- Endpoints that return HTML are intended for browser use.
- All API responses are JSON unless rendering a template.

---
