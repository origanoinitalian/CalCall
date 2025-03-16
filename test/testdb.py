from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load the DATABASE_URL from .env
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Create an engine and test the connection
try:
    engine = create_engine(DATABASE_URL)
    connection = engine.connect()
    print("Database connection successful!")
    connection.close()
except Exception as e:
    print(f"Error connecting to the database: {e}")