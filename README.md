# Project Title 🎓

**Mini Social Media API**

---

## Description 📝
This is a mini social media api where users can interact with their favourite users, upload profile pictures and view posts made by followers and non-followers.

---

## Technology Stack 🛠️

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-2C3E50?style=for-the-badge&logo=pydantic&logoColor=white)
![Postgres](https://img.shields.io/badge/Postgres-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white)
![Sentry](https://img.shields.io/badge/Sentry-362D59?style=for-the-badge&logo=sentry&logoColor=white)

---

## Features ✨

### RBAC (users, admin)

#### Users:
- Create account and view profile with profile images
- View feed posts from followers and non-followers
- Like and comment on a post
- Follow and unfollow other users
- View followers and followings

#### Admin:
- Assign admin role
- Suspend and unsuspend users
- View and manage list of active users
- View and manage list suspended users

---

To run application locally

### Prerequisites 📋

- Install Python 3.14. [Installation link](https://www.python.org/downloads/)
- Install and set up RabbitMQ on your machine. [Installation link](https://www.rabbitmq.com/docs/download)
- Install and set up PgAdmin. [Installation link](https://www.pgadmin.org/download/)

---

### Steps 🛠️

#### Clone the repository:
```bash
git clone `https://github.com/Samson23-ux/Social-Media-API`
```

#### Navigate to the project directory:
```bash
cd "Social-Media-API"
```

#### Create and activate virtual environment:

**Create:**
```bash
python -m venv venv
```

**Activate:**
- **Windows:**
```bash
venv\Scripts\activate
```
- **Linux/macOS:**
```bash
source venv/bin/activate
```

#### Install dependencies:
```bash
pip install -r requirements.txt
```

#### Set up environment variables:
- Set the environment variables in the `env-demo.txt` file ([link to file](./env-demo.txt))

#### Create API database using PgAdmin.

#### Run Python script to initialize the database with roles and set admin details:
```bash
python -m app.scripts.seed_data
```

#### Start Celery worker:
```bash
celery -A app.schedules.celery_app worker -l info -P gevent
```

#### Start Celery beat:
```bash
celery -A app.schedules.celery_app beat -l info
```

#### Run the application:
```bash
uvicorn app.main:app --reload
```

#### Test API endpoints via docs:
Open your browser and navigate to [http://localhost:8000/docs](http://localhost:8000/docs).

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
pytest tests/<preferred_test_file.py>::<preferred_test>
```
