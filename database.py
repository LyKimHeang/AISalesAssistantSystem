import sqlite3

# connect to database
conn = sqlite3.connect('store.db')

# create cursor
cursor = conn.cursor()

# create products table
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    stock INTEGER,
    price REAL
)
''')

# insert sample data
cursor.execute('''
INSERT INTO products (name, stock, price)
VALUES ('iPhone 15', 5, 1200)
''')

cursor.execute('''
INSERT INTO products (name, stock, price)
VALUES ('Laptop', 3, 900)
''')

# save changes
conn.commit()

# close database
conn.close()

print("Database created successfully!")