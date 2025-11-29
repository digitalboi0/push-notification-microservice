# Use a Python runtime as the parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory in the container
WORKDIR /app

# Install system dependencies required at runtime
# Example: If using psycopg2-binary, you might not strictly need libpq5 at runtime,
# but if using psycopg2 (source build), you would need it installed here.
# Example: If using other C libraries, install them here.
# Example: If using git inside the container for some reason during runtime/build
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     libpq5 \
#     git \
#     && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . /app/

# --- Static Files for Admin (Still needed if using admin) ---
# Collect static files during the build process.
# This ensures the admin panel works if accessed.
# The STATIC_ROOT directory will be created and populated here.
# Replace 'push.settings' with your actual main settings module path if different
# (e.g., if you have a base settings and production inherits from it).
RUN python manage.py collectstatic --noinput --settings=push.settings

# --- User Creation (Security Best Practice) ---
# Create a non-root user to run the application
RUN useradd --create-home --shell /bin/bash appuser
# Change ownership of the /app directory to the new user
RUN chown -R appuser:appuser /app
# Switch to the new user
USER appuser

# Expose the port the app runs on
EXPOSE 8000

# Define the command to run the application server (Gunicorn for production)
CMD ["gunicorn", "push.wsgi:application", "--bind", "0.0.0.0:8000"]


# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]