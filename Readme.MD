# Site Audit AI Push Notification Service

This Django-based service handles sending push notifications to Android (FCM), iOS (APNs), and Web (VAPID) platforms using a unified API. It leverages Celery for asynchronous task processing and Redis for task queuing.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Features

*   **Multi-Platform Support:** Send push notifications to Android, iOS, and Web browsers.
*   **Unified API:** Single endpoint to manage notifications across all platforms.
*   **Template System:** Pre-defined templates for common notification types with dynamic placeholders.
*   **Asynchronous Processing:** Uses Celery and Redis for non-blocking notification sending.
*   **Device Management:** Stores and manages device tokens per application and user.
*   **Activity Logging:** Logs all notification sending attempts and outcomes.
*   **App-Based Authentication:** Secures API endpoints using unique App Keys.

## Tech Stack

*   **Backend:** [Python](https://www.python.org/downloads/) (3.8+)
*   **Framework:** [Django](https://www.djangoproject.com/)
*   **API Framework:** [Django REST Framework](https://www.django-rest-framework.org/)
*   **Database:** [PostgreSQL](https://www.postgresql.org/) (recommended for production) or [SQLite](https://www.sqlite.org/index.html) (for development)
*   **Task Queue:** [Celery](https://docs.celeryq.dev/)
*   **Message Broker:** [Redis](https://redis.io/)
*   **Web Server:** [Gunicorn](https://gunicorn.org/) (for production)
*   **Frontend:** [HTML/CSS/JavaScript](https://developer.mozilla.org/en-US/docs/Web) (for testing web push subscription)

## Prerequisites

*   Python 3.8+
*   PostgreSQL server (for production) or SQLite (included with Python)
*   Redis server
*   Git (optional, for cloning the repository)

## Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/push_notification_service.git
    cd push_notification_service
    ```

2.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  **Environment Variables:**
    Create a `.env` file in the project root directory (`push_notification_service/.env`) and add the following variables (replace placeholders with your actual values):

    ```ini
    # Django Settings
    SECRET_KEY=your_django_secret_key_here
    DEBUG=False # Set to True for development, False for production
    ALLOWED_HOSTS=localhost,127.0.0.1,your_domain.com # Comma-separated list
    DB_NAME=push_notifications
    DB_USER=your_db_username
    DB_PASSWORD=your_db_password
    DB_HOST=localhost
    DB_PORT=5432 # Default PostgreSQL port
    REDIS_URL=redis://localhost:6379/0 # Update if Redis is on a different host/port

    # CORS Settings (if needed)
    CORS_ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend-domain.com # Comma-separated list

    # FCM Settings (for Android)
    FCM_SERVER_KEY=your_fcm_server_key_here

    # APNs Settings (for iOS)
    APNS_CERT_PATH=/path/to/your/apns_certificate.pem # Path to .pem file
    APNS_TOPIC=your_app_bundle_id

    # Web VAPID Settings (for Web Push)
    WEB_VAPID_PUBLIC_KEY=your_vapid_public_key
    WEB_VAPID_PRIVATE_KEY=your_vapid_private_key
    ```

2.  **Database Migration:**
    Apply the database schema changes defined in the models.
    ```bash
    python manage.py migrate
    ```

3.  **Create Superuser (Optional):**
    Create an admin user to access the Django admin panel for managing Apps, Devices, Templates, and Logs.
    ```bash
    python manage.py createsuperuser
    ```

## Running the Application

### Development

1.  **Start the Django Development Server:**
    ```bash
    python manage.py runserver
    ```
    The application will be accessible at `http://127.0.0.1:8000/`.

2.  **Start the Celery Worker:**
    In a *separate* terminal, ensure the virtual environment is activated and run:
    ```bash
    celery -A push worker --loglevel=info --settings=push.settings
    ```
    This worker handles the asynchronous sending of push notifications.

### Production

1.  **Install Production Requirements:**
    If your `requirements.txt` separates development and production dependencies, install the production ones:
    ```bash
    pip install gunicorn
    # Add other production-specific packages as needed
    ```

2.  **Collect Static Files:**
    Django needs to gather all static files (CSS, JS, images) into a single location for the web server.
    ```bash
    python manage.py collectstatic --noinput
    ```

3.  **Start the Web Server (Gunicorn):**
    ```bash
    gunicorn push.wsgi:application --bind 0.0.0.0:8000
    ```
    It's recommended to use a process manager like `supervisor` or run this behind a reverse proxy like Nginx.

4.  **Start Celery Worker (Production):**
    Run the Celery worker in the background using a process manager (e.g., supervisor, systemd).
    ```bash
    celery -A push worker --loglevel=info --settings=push.settings
    ```
    Also, start the Celery Beat scheduler if you have periodic tasks:
    ```bash
    celery -A push beat --loglevel=info --settings=push.settings
    ```

5.  **Configure Reverse Proxy (Nginx Example):**
    Set up Nginx to serve static files and proxy requests to your Gunicorn server. Example Nginx configuration (`/etc/nginx/sites-available/push_service`):
    ```nginx
    server {
        listen 80;
        server_name your_domain.com;

        location /static/ {
            alias /path/to/your/project/staticfiles/; # Update path
        }

        location / {
            proxy_pass http://127.0.0.1:8000; # Gunicorn bind address
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
    ```
    Enable the site and restart Nginx:
    ```bash
    sudo ln -s /etc/nginx/sites-available/push_service /etc/nginx/sites-enabled
    sudo systemctl restart nginx
    ```

## API Documentation

See the `api_docs.html` file included in the project for detailed API documentation, including endpoints, request/response formats, and examples.

## Deployment

### Docker (Optional)

1.  **Build the Docker Image:**
    ```bash
    docker build -t push_notification_service .
    ```

2.  **Run the Application:**
    You'll need to run the Django app, Celery worker, and Redis. Consider using `docker-compose` for easier orchestration.

    Example `docker-compose.yml`:
    ```yaml
    version: '3.8'

    services:
      db:
        image: postgres:15
        volumes:
          - postgres_/var/lib/postgresql/data/
        environment:
          - POSTGRES_DB=push_notifications
          - POSTGRES_USER=postgres
          - POSTGRES_PASSWORD=postgres
        ports:
          - "5432:5432"

      redis:
        image: redis:7-alpine
        ports:
          - "6379:6379"

      web:
        build: .
        command: gunicorn push.wsgi:application --bind 0.0.0.0:8000
        volumes:
          - .:/app
        ports:
          - "8000:8000"
        environment:
          - DEBUG=0
          - DB_HOST=db
          - REDIS_URL=redis://redis:6379/0
          # Add other environment variables
        depends_on:
          - db
          - redis

      worker:
        build: .
        command: celery -A push worker --loglevel=info
        volumes:
          - .:/app
        environment:
          - DB_HOST=db
          - REDIS_URL=redis://redis:6379/0
          # Add other environment variables
        depends_on:
          - db
          - redis

      beat:
        build: .
        command: celery -A push beat --loglevel=info
        volumes:
          - .:/app
        environment:
          - DB_HOST=db
          - REDIS_URL=redis://redis:6379/0
          # Add other environment variables
        depends_on:
          - db
          - redis

    volumes:
      postgres_
    ```

    Run with:
    ```bash
    docker-compose up -d
    ```

### Environment-Specific Considerations

*   **Security:** Ensure `DEBUG=False`, use strong passwords, configure allowed hosts, and use HTTPS in production.
*   **Performance:** Optimize database queries, use caching, scale Celery workers, and configure your web server appropriately.
*   **Monitoring:** Implement logging, error tracking, and performance monitoring.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)