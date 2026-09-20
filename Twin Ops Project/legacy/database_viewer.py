import sqlite3

connection = sqlite3.connect("twinops.db")
cursor = connection.cursor()

cursor.execute("""
    SELECT *
    FROM sensor_data
    ORDER BY id DESC
    LIMIT 10
""")

rows = cursor.fetchall()

print("\n===== TWIN OPS SENSOR DATA =====\n")

for row in rows:
    print(row)

connection.close()