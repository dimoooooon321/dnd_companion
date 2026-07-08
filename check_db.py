from sqlalchemy import create_engine, text

engine = create_engine(
    "postgresql://postgres:postgres@127.0.0.1:5432/dnd_companion"
)

with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE direct_test (
            id INTEGER
        )
    """))

print("DONE")