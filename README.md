# Project Title
Mini Social Media API

## Description

Provide a brief description of the project, its purpose, and what it aims to achieve.


## Features

- List the key features of the project.
- Highlight what makes it unique or useful.

## Ways to run application
1. Run application locally

   ### Prerequisites
   - Specify any prerequisites (e.g., Python version, Docker, etc.)
   - Install Python 3+. Installation link: <insert official python installation link>
   - Install and setup RabbitMQ on machine. Installation link: <insert official rabbitmq installation link>
   - Install and setup PgAdmin. Installation link: <insert official pgadmin installation link>

   ### Steps
   1. Clone the repository:
      ```bash
      git clone <repository-url>
      ```
   2. Navigate to the project directory:
      ```bash
      cd "Mini Social Media API"
      ```
   3. Install dependencies:
      ```bash
      pip install -r requirements.txt
      ```
   4. Set up environment variables:
      - Provide details on `.env` file or other configurations.
      - Set the enviroment variables below

      ENVIROMENT=development

      # Fastapi port
      API_PORT=8000

      # API DB 
      API_DB=your_db_name
      API_DB_USER=your_db_user
      API_DB_PASSWORD=your_db_password
      API_DB_PORT=your_api_db_port

      # Test DB
      Create a separate database to run tests
      TEST_DB=your_db_name
      TEST_DB_USER=your_db_user
      TEST_DB_PASSWORD=your_db_password
      TEST_DB_PORT=your_test_db_port

      # RabbitMQ 
      BROKER_USER=your_broker_user
      BROKER_PASSWORD=your_broker_password
      BROKER_VHOST=your_broker_virtual_host
      BROKER_PORT=broker_port
      BROKER_PLUGIN_PORT=broker_plugin_port

      # Database urls
      DATABASE_URL=postgresql+psycopg://{API_DB_USER}:{API_DB_PASSWORD}@localhost:5432/{API_DB}
      WORKER_DATABASE_URL=postgresql+psycopg2://{API_DB_USER}:{API_DB_PASSWORD}@localhost:5432/{API_DB}
      TEST_DATABASE_URL=postgresql+psycopg2://{TEST_DB_USER}:{TEST_DB_PASSWORD}@localhost:5432/{TEST_DB}

      # RabbitMQ url
      BROKER_URL=amqp://{BROKER_USER}:{BROKER_PASSWORD}@localhost:5672/{BROKER_VHOST}

      # Argon2
      ARGON2_PEPPER=your_argon2_pepper

      # Authentication
      JWT_ALGORITHM=jwt_algorithm
      ACCESS_TOKEN_SECRET_KEY=your_access_token_secret_key
      ACCESS_TOKEN_EXPIRE_TIME=your_access_token_expire_time
      REFRESH_TOKEN_SECRET_KEY=your_refresh_token_secret_key
      REFRESH_TOKEN_EXPIRE_TIME=your_refresh_token_expire_time

      # Admin
      ADMIN_DISPLAY_NAME=your_admin_display_name
      ADMIN_USERNAME=your_admin_username
      ADMIN_EMAIL=your_admin_email
      ADMIN_PASSWORD=your_admin_password
      ADMIN_DOB=your_admin_dob
      ADMIN_NATIONALITY=your_admin_nationality
      ADMIN_BIO=your_admin_bio

      - Use set admin deatils to perform admin related actions

      # Image Uploads
      PROFILE_IMAGE_PATH=profile_image_path 
         - NB: use ./app/uploads/profile_images/
      POST_IMAGE_PATH=post_image_path
         - NB: use ./app/uploads/post_images/

      # Sentry DSN
      SENTRY_SDK_DSN=your_sentry_dsn
         - Get a sentry dsn at <Insert sentry link>

   5. Run python script to initialize database with the set admin details
      ```bash
      python -m app.scripts.seed_data
      ```

   6. Start celery worker
      ```bash
      Celery -A app.schedules.celery_app worker -l info -P gevent
      ```

   8. Start celery beat
      ```bash
      Celery -A app.schedules.celery_app beat -l info
      ```

   9. Run the application:
      ```bash
      uvicorn app.main:app --reload
      ```

   10. Test API endpoints via docs
      Open browser and navigate to http://localhost:8000/docs

2. Run application via docker

   # Prerequisites
   - Setup docker on machine. See <insert docker official download link>

   - Navigate to command line
   - Run:
      ```bash
      docker compose up
      ```
   -  Open browser and navigate to http://localhost:8000/docs to test endpoints

3. Test endpoints via live url
   NB: Some services are hosted are on free tier and may not be available after a few days
   - Live url: <Insert live url>

## Testing

1. Run tests:
   ```bash
   pytest
   ```
2. Run tests with coverage:
   ```bash
   pytest --cov=.
   ```
3. Run a particular test
   ```bash
   pytest tests/<preferred_test_folder>::<preferred_test_file.py>
   ```

## License

Specify the license under which the project is distributed.
