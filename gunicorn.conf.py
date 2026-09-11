import os

# Server socket binding
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"

# Worker processes and threads
workers = int(os.getenv("WEB_CONCURRENCY", "2"))
threads = int(os.getenv("PYTHON_THREADS", "4"))
worker_class = "gthread"
timeout = int(os.getenv("GUNICORN_TIMEOUT", "120"))
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")
