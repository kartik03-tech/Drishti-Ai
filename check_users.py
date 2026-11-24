import sqlite3
import os

DB = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "database.db"
)

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

rows = conn.execute(
    """
    SELECT id, name, email
    FROM users
    ORDER BY id
    """
).fetchall()

print("\n========== REGISTERED USERS ==========")

for row in rows:
    print(
        f"ID: {row['id']} | "
        f"Name: {row['name']} | "
        f"Email: {row['email']}"
    )

print("======================================\n")

conn.close()