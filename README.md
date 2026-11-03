# GST Billing Application

A production-grade GST billing application for Indian businesses. Create professional tax invoices, manage customers and products, calculate GST automatically, generate PDFs, and maintain complete invoice history.

## Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI, SQLAlchemy 2.x, Pydantic v2 |
| Database | MySQL 8.x (utf8mb4, DECIMAL for money) |
| Migrations | Alembic |
| Frontend | HTML5, CSS3, JavaScript ES6+ |
| Auth | JWT (access + refresh tokens) |
| PDF | WeasyPrint |

## Quick Start

### Prerequisites

- Python 3.11+
- MySQL 8.x
- pip

### Setup

```bash
# 1. Clone the repository
cd HawlMark

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
cd backend
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your MySQL credentials

# 5. Create MySQL database
mysql -u root -e "CREATE DATABASE gst_billing CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -e "CREATE USER 'MYSQL_USER'@'localhost' IDENTIFIED BY 'MYSQL_PASSWORD';"
mysql -u root -e "GRANT ALL PRIVILEGES ON gst_billing.* TO 'MYSQL_USER'@'localhost';"

# 6. Run migrations
alembic upgrade head

# 7. Start the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```


''' cd /Users/rishabhgoyal/Desktop/HawlMark/backend
source ../venv/bin/activate
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000;   ''' 

### Access

- Application: http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- Health Check: http://localhost:8000/api/health

## Project Structure

```
HawlMark/
├── requirements/          # Specification documents
├── backend/
│   ├── app/
│   │   ├── main.py        # FastAPI application
│   │   ├── config/        # Settings from .env
│   │   ├── database/      # SQLAlchemy engine/session/base
│   │   ├── models/        # Database models
│   │   ├── schemas/       # Pydantic request/response schemas
│   │   ├── routes/        # API endpoints
│   │   ├── services/      # Business logic
│   │   ├── auth/          # JWT authentication
│   │   └── utils/         # Validators, exceptions, helpers
│   ├── migrations/        # Alembic migrations
│   ├── tests/             # pytest test suite
│   └── .env.example       # Environment template
├── frontend/
│   ├── templates/         # Jinja2 HTML templates
│   └── static/            # CSS, JS, assets
└── docs/                  # Documentation
```

## Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

## License

Private — All rights reserved.
