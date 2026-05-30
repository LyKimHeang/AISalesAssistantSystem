import sqlite3

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

DATABASE = "store.db"


def get_connection():
    return sqlite3.connect(DATABASE)

def create_default_admin():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE role='seller'"
    )

    admin = cursor.fetchone()

    if not admin:

        hashed_password = generate_password_hash(
            "admin123"
        )

        cursor.execute("""
        INSERT INTO users(
            email,
            password,
            role
        )
        VALUES (?, ?, ?)
        """, (
            "admin@store.com",
            hashed_password,
            "seller"
        ))

        conn.commit()

    conn.close()

def create_user(email, password):

    hashed_password = generate_password_hash(
        password
    )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO users(
        email,
        password,
        role
    )
    VALUES (?, ?, ?)
    """, (
        email,
        hashed_password,
        "buyer"
    ))

    conn.commit()
    conn.close()
    
def get_user_by_email(email):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
    )

    user = cursor.fetchone()

    conn.close()

    return user

def verify_user(email, password):

    user = get_user_by_email(email)

    if not user:
        return None

    stored_password = user[2]

    if check_password_hash(
        stored_password,
        password
    ):
        return user

    return None

def get_all_products():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()

    conn.close()

    return products

def search_product(product_name):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM products
        WHERE LOWER(name) LIKE LOWER(?)
        """,
        (f"%{product_name}%",)
    )

    product = cursor.fetchone()

    conn.close()

    return product

def add_product(name, stock, price):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO products(name, stock, price)
        VALUES (?, ?, ?)
        """,
        (name, stock, price)
    )

    conn.commit()
    conn.close()

def delete_product(product_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM products WHERE id = ?",
        (product_id,)
    )

    conn.commit()
    conn.close()

def get_product_by_id(product_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    )

    product = cursor.fetchone()

    conn.close()

    return product

def update_product(product_id, name, stock, price):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE products
        SET name=?, stock=?, price=?
        WHERE id=?
        """,
        (name, stock, price, product_id)
    )

    conn.commit()
    conn.close()
    
def initialize_database():

    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)

    # Products table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        stock INTEGER NOT NULL,
        price REAL NOT NULL
    )
    """)

    conn.commit()
    conn.close()