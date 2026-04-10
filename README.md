# Berry Street - Paper Trading Platform 📈

Welcome to **Berry Street**, a robust and blazing fast paper trading backend crafted specifically for the Indian Stock Market. Built with modern Python and FastAPI, this application allows users to simulate stock trading using real-time market data without risking real money.

## 🚀 Features

*   **OAuth Authentication:** Secure user registration and login via JWT tokens.
*   **Virtual Wallet:** Every new user starts with a ₹1,00,000 INR practice balance.
*   **Live Market Data:** Fetches real-time stock quotes and historical chart data via `yfinance`.
*   **Trade Execution:** Buy and sell orders are validated against the user's wallet balance and portfolio holdings.
*   **Portfolio Management:** Track your current holdings, average buy prices, and overall portfolio performance.
*   **ACID Compliant:** Powered by SQLAlchemy to ensure transaction integrity (if a trade fails midway, the database rolls back seamlessly).

## 🛠️ Technology Stack

*   **Framework:** FastAPI (High performance, async-ready, built-in Swagger UI)
*   **Database:** SQLite (Local testing) / SQLAlchemy (ORM)
*   **Data Validation:** Pydantic
*   **Market Data:** Yahoo Finance API (`yfinance`)
*   **Security:** PyJWT & OAuth2

## 📦 Installation & Setup

1. **Clone the repository and enter the directory:**
   ```bash
   git clone <repository-url>
   cd BerryStreet
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   
   # For Windows:
   .venv\Scripts\activate
   # For macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the development server:**
   ```bash
   fastapi dev app/main.py
   ```
   *Note: Using `fastapi dev` provides hot-reloading out of the box.*

## 📖 API Documentation

Once the server is running, FastAPI automatically generates interactive API documentation. 
Navigate to your browser to view and test endpoints directly:

*   **Swagger UI (Interactive):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
*   **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## 🧪 Testing the Flow

A `test_script.py` is included in the project root to automate an end-to-end user flow:
1. It registers/authenticates a test user.
2. Fetches a market quote (e.g., RELIANCE.NS).
3. Executes a BUY order.
4. Executes a SELL order.
5. Prints the finalized portfolio holdings.

Run the script locally while the server is running:
```bash
python test_script.py
```

## 🏗️ Architecture Note

This project is structured using best practices to separate concerns:
*   `models.py`: Database table definitions (SQLAlchemy).
*   `schemas.py`: Data validation blueprints (Pydantic).
*   `database.py`: DB Connection, Engine, and Session Dependency injection (`get_db`).
*   `routers/`: Modular route handlers for `/users`, `/market`, `/trading`, and `/portfolio`.
