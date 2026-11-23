# Asset Health Management System (AHMS)

The **Asset Health Management System (AHMS)** is a web application and pure Python OOP analytics engine designed to help individuals record, monitor, and assess their complete asset portfolio (both financial and physical assets) in Pakistani Rupee (PKR).

AHMS evaluates portfolio health across six core dimensions (Profitability, Diversification, Liquidity, Risk, Growth, and Income) to compute an objective **Asset Health Score (0–100)** with tailored, plain-language decision-support recommendations.

---

## Tech Stack
- **Backend**: Python 3.13, Django
- **Analytics Engine**: Pure Python OOP (`analytics/`), strictly using `Decimal` for all money math (no Django dependencies)
- **Database**: SQLite (local development) / PostgreSQL (production ready)
- **Frontend**: Django Templates, Tailwind CSS, Chart.js
- **Testing**: `pytest`, `pytest-django`
- **Configuration & Security**: `python-dotenv`, secrets isolated in `.env`

---

## Project Structure

```
AHMS/
│
├── config/             # Django settings, root URLs, WSGI/ASGI configuration
├── accounts/           # User authentication (signup, login, logout, password reset)
├── portfolio/          # Asset tracking, transactions, valuations, and income records
├── analytics/          # Pure Python OOP financial & risk engine (no Django imports)
├── market_data/        # MarketDataService and automated price retrieval commands
├── reports/            # PDF and CSV report generation
├── templates/          # Global templates & app-level template overrides
├── static/             # Static assets (CSS, JS, images)
├── tests/              # Test suites (analytics engine, Django views, permissions)
├── .env.example        # Environment variable template
├── .gitignore          # Git exclusion rules
├── pytest.ini          # Pytest and pytest-django configuration
├── requirements.txt    # Project Python dependencies
└── manage.py           # Django management CLI
```

---

## Getting Started

### 1. Clone the repository
```bash
git clone <repository-url>
cd AHMS
```

### 2. Set up virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Copy `.env.example` to `.env`:
```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

### 5. Run database migrations
```bash
python manage.py migrate
```

### 6. Run the development server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

### 7. Run test suite
```bash
pytest
```
