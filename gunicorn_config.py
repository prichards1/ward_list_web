# gunicorn_config.py

# Socket Path: Gunicorn will create this file to talk to Nginx
# In Docker, we usually use a TCP port (0.0.0.0:8000), but for local services 
# or specific setups, we can use unix sockets. 
# Since we are moving to Docker next, let's use TCP port binding.
bind = "0.0.0.0:8000"

# Workers: Formula is usually (2 x CPUs) + 1
workers = 4

# Threads: If your app handles I/O (like file uploads), threads help prevent blocking
threads = 2

# Timeout: Uploading large CSVs might take time, so let's increase this from default 30s
timeout = 120

# Logging
accesslog = "-"  # Print to stdout
errorlog = "-"   # Print to stderr
loglevel = "info"