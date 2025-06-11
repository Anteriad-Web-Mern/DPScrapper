# 🕸️ DPScrapper

**DPScrapper** is a Python-based web scraping and automation project built to extract and manage data from multiple WordPress sites efficiently. It also includes integration with **Google Analytics (GA4)** to fetch analytical reports and a **cache-clearing** feature for Kinsta-hosted sites.


![MIT License](https://img.shields.io/github/license/Anteriad-Web-Mern/DPScrapper)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![JavaScript](https://img.shields.io/badge/logo-javascript-blue?logo=javascript)

---
## Table of Contents
- [Features](#Features)
- [Setup Instructions](#setup-instructions)
- [Usage](#how-to-use)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
---

## 🚀 Features

- 🔍 Scrape WordPress-based websites via REST API
- 👥 Bulk user creation for multiple domains
- 🧼 Kinsta cache clearing using their API
- 📊 Google Analytics GA4 integration
- 📁 Modular and extensible architecture
- 🛡️ Secure handling of service account credentials

---

## 📁 Project Structure
```
DPScrapper/
          ├── analytics_report.py            # GA4 reporting logic
          ├── app.py                         # Flask-based API
          ├── bulk_user_add.py               # Bulk user creation script
          ├── clear_cache.py                 # Kinsta cache clearing logic
          ├── domains.json                   # List of domains to target
          ├── service-account.json           # Google service credentials (should be gitignored)
          ├── requirements.txt               # Project dependencies
          └── README.md                      # Project documentation
```
---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Anteriad-Web-Mern/DPScrapper.git
cd DPScrapper
```


### 2. Create Virtual Environment
   
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Prepare Configuration Files

- Create a **service-account.json** file in the root directory (this is required for **GA4**).
- Update **domains.json** with your list of WordPress domains and credentials:
```json
[
  {
    "url": "https://example.com",
    "username": "admin",
    "password": "yourpassword"
  }
]
```

## 🧪 How to Use

### 1. Run Flask Server

```bash
python app.py
```

### 2. Clear Kinsta Cache

```bash
curl -X POST http://localhost:5000/clear-cache/yourdomain.com
```

### 3. Generate Google Analytics Report

```bash
python analytics_report.py
```

### 4.📡 API Endpoints

| Endpoint                   | Method | Description                        |
|----------------------------|--------|------------------------------------|
| /clear-cache/<domain>      | POST   | Clears Kinsta cache for site       |
| /bulk-add-user             | POST   | Adds users to all domains          |

#### Example
```bash
curl -X POST http://localhost:5000/clear-cache/example.com
```

### 5. 📈 Google Analytics Integration
- Uses GA4 Data API
- Requires a service account file from Google Cloud Console
- You can customize:
    1. Metrics: sessions, activeUsers, etc.
    2. Dimensions: date, country, deviceCategory
    3. Date ranges and filters

## 🔐 Remove Sensitive Files from Git History
If you've accidentally committed sensitive files like service-account.json:

```json
git rm --cached service-account.json
echo "service-account.json" >> .gitignore
git commit -m "Remove sensitive file from tracking"
git push origin main
```
## 🔮 Future Plans
- Web dashboard for report visualization
- Docker support for easy deployment
- Logging and analytics tracking interface
- Email notifications for automation tasks

### 🤝 Contributing
- Contributions are welcome! Please fork the repository and open a pull request. Make sure your code follows good practices and includes documentation.

### 📜 License
- This project is licensed under the MIT License.

### 📬 Contact
- Maintained by Anteriad Web Team
```bash
GitHub: https://github.com/Anteriad-Web-Mern
```

---
