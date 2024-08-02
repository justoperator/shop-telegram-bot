#CODE FOR WHAT CREATE database.db !!DATABASE ALREADY CREATE AND WORK, USE IT ONLY IF YOU DELETE DATABASE AND WANT GET BACK IT!!

import sqlite3

conn = sqlite3.connect('database/database.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users(
               user TEXT,
               areact TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS products(
               name TEXT,
               description TEXT,
               price TEXT,
               category TEXT,
               image TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS orders(
               name TEXT,
               username TEXT,
               id TEXT,
               phonenumber TEXT,
               product TEXT
)
''')

conn.commit()
conn.close()