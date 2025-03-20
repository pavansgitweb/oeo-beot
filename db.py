import sqlite3

connection = sqlite3.connect('xp_data.db')
cursor = connection.cursor()
cursor.execute("ALTER TABLE xp_data ADD COLUMN bank INTEGER DEFAULT 0")
connection.commit()

