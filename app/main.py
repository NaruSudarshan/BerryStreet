from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import market, users, trading, portfolio
from app.database import engine
from app import models

# CRITICAL LINE: This looks at models.py and creates the actual SQLite tables.
# It must come BEFORE the app = FastAPI() initialization.
models.Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Berry Street", 
    version="1.0.0",
    description="A paper trading platform for the Indian Stock Market."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Plug in the routers so they show up in Swagger UI
app.include_router(users.router)
app.include_router(market.router)
app.include_router(trading.router)
app.include_router(portfolio.router)

@app.get("/")
def home():
    return {"message": "Welcome to Berry Street! The Grand Line of Trading."}