import psycopg2

try:
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        user="postgres",
        password="postgres",
        dbname="dnd_companion"
    )
    print("SUCCESS")

except Exception as e:
    print("TYPE:", type(e))
    print("ARGS:", e.args)

    if hasattr(e, "pgerror"):
        print("PGERROR:", e.pgerror)

    if hasattr(e, "diag"):
        print("DIAG:", e.diag)