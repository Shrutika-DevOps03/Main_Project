import os
import oracledb
from dotenv import load_dotenv

load_dotenv()

conn = oracledb.connect(
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    dsn=os.getenv("DB_DSN"),
)

cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM orders")
print("Orders in database:", cursor.fetchone()[0])

cursor.close()
conn.close()
