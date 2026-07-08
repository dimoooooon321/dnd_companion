from app.core.config import settings
from sqlalchemy import create_engine, text

print("DATABASE_URL =", settings.DATABASE_URL)

engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print(result.scalar())