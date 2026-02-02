# Ward List Quiz Web App

A secure, containerized web application designed to help ward leaders and clerks learn the names and faces of ward members. The app parses a standard CSV export from LCR (Leader and Clerk Resources) and generates an interactive quiz.

![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11-yellow.svg)
![Flask](https://img.shields.io/badge/Framework-Flask-green.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)

## 📋 Table of Contents
- [Architecture](#-architecture)
- [Quick Start (Portainer)](#-quick-start-portainer)
- [Manual Deployment (CLI)](#-manual-deployment-cli)
- [Configuration](#-configuration)
- [Data Procedure (Usage)](#-data-procedure-how-to-use)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)

---

## 🏗 Architecture

The application runs as a multi-container Docker stack:
1.  **App Container (`ward_list_app`):** Runs the Python Flask application served by Gunicorn.
2.  **Proxy Container (`ward_list_nginx`):** An Nginx reverse proxy that handles external traffic and routes it to Gunicorn.

**Security Features:**
* **Ephemeral Data:** No database is used. The CSV data exists only in the user's active session and is wiped on restart/logout.
* **Auto-Secrets:** The app automatically generates cryptographically secure session keys on startup if none are provided.

---

## 🚀 Quick Start (Portainer)

This is the recommended deployment method.

1.  **Log in to Portainer** and go to **Stacks** → **Add Stack**.
2.  **Name:** `ward-list-quiz` (or your preference).
3.  **Build Method:** Select **Repository**.
4.  **Repository URL:** `https://github.com/prichards1/ward_list_web.git`
5.  **Repository Reference:** `refs/heads/main`
6.  **Environment Variables:** *None required.*
    * *Default Port:* `8625`
    * *Secret Key:* Auto-generated.
7.  Click **Deploy the stack**.

The app will be available at: `http://<your-server-ip>:8625`

---

## 💻 Manual Deployment (CLI)

If you prefer using the command line or don't use Portainer:

```bash
# 1. Clone the repo
git clone https://github.com/prichards1/ward_list_web.git
cd ward_list_web

# 2. Start the stack
docker compose up --build -d

# 3. Verify
docker compose ps
```

---

## ⚙ Configuration

You can customize the deployment using Environment Variables in `docker-compose.yml` or Portainer.

| Variable | Default | Description |
| :--- | :--- | :--- |
| `WARD_QUIZ_PORT` | `8625` | The external port on the host machine. |
| `FLASK_SECRET_KEY` | *(Random Hex)* | Used to sign session cookies. If empty, a secure random key is generated on boot. |

---

## 📝 Data Procedure (How to Use)

The application requires a CSV file exported from ChurchofJesusChrist.org. **This file must be cleaned before upload.**

### Step 1: Export Data
1.  Log in to **[LCR (Leader and Clerk Resources)](https://lcr.churchofjesuschrist.org/)**.
2.  Go to **Membership** → **Member List**.
3.  Click **Print/Export** → **Export to CSV**.

### Step 2: Clean the Data
The raw export contains metadata headers (Ward Name, Date) that must be removed.

**Option A: Manual Method**
Open in Excel/Numbers, delete the top rows until the header row (starting with "Preferred Name") is in **Row 1**. Save as CSV.

**Option B: Script Method (Recommended)**
Use the included helper script `clean_ward_list.py`.
```bash
python3 clean_ward_list.py <path_to_downloaded_csv>
```

### Step 3: Upload & Quiz
1.  Open the web app (`http://<server-ip>:8625`).
2.  Upload the **cleaned** CSV file.
3.  Start the quiz!

---

## 🛠 Development

To work on the code locally:

1.  **Clone the repo:**
    ```bash
    git clone https://github.com/prichards1/ward_list_web.git
    ```
2.  **Edit `docker-compose.yml`:**
    Uncomment the `volumes` section for the `app` service to enable "hot reloading" (changes on your laptop reflect instantly in the container).
    ```yaml
    volumes:
       - ./:/app  # Uncomment for Dev
    ```
3.  **Run:** `docker compose up`

---

## ❓ Troubleshooting

**"RuntimeError: The session is unavailable..."**
* **Cause:** The application received an empty environment variable string.
* **Fix:** The code has been patched to handle this, but you can also manually add `FLASK_SECRET_KEY` = `some_random_string` in Portainer variables.

**"gunicorn_config.py doesn't exist"**
* **Cause:** The file wasn't pushed to Git, or a volume mount is hiding it.
* **Fix:** Ensure the file is in the repo (`git ls-files`) and that you are NOT mounting local volumes in a Production deployment.

**"services.app additional properties 'nginx' not allowed"**
* **Cause:** Indentation error in `docker-compose.yml`.
* **Fix:** Ensure `nginx:` is at the same indentation level as `app:`, not nested inside it.