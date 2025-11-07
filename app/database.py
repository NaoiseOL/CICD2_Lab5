import os, time
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import session_maker
from sqlalchemy.exc import OperationalError

envfile = {
    "dev": ".env.dev",
    "docker": ".env.docker",
    "test": ".env.test",
}.get(os.getenv("APP_ENV", "dev"), ".env.dev")
load_dotenv(envfile, override=True)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
SQL_ECHO = os.getenv("SQL_ECHO", "false").lower() == "true"
RETRIES = int(os.getenv("DB_RETRIES", "10"))
DELAY = float(os.getenv("DB_RETRY_DELAY", "1.5"))

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

for _ in range(RETRIES):
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=SQL_ECHO,
connect_args=connect_args)
        with engine.connect():
            pass
        break
    except OperationalError:
        time.sleep(DELAY)
Sessionlocal = sessionmaker(bind=engine, autocommit=False, autoflush=False,
expire_on_commit=False)

def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close