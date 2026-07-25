import sqlite3

DB_PATH = r"D:\homework\legal-ai\backend\legal_ai.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
print(cur.execute("PRAGMA table_info(comparisons)").fetchall())
conn.close()
