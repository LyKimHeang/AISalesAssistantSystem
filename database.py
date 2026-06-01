import sqlite3
import re

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

def search_product(query):

    conn = get_connection()
    cursor = conn.cursor()

    # 1st try: search the full query as-is
    cursor.execute(
        "SELECT * FROM products WHERE LOWER(name) LIKE LOWER(?)",
        (f"%{query}%",)
    )
    product = cursor.fetchone()

    # 2nd try: if no match, split into words and try each one
    # This handles full sentences like "do you have laptop?"
    if not product:
        words = query.split()
        for word in words:
            # Strip punctuation (removes "?" "!" "." etc.)
            clean_word = re.sub(r'[^\w]', '', word)
            # Skip very short words like "do", "a", "is", "the"
            if len(clean_word) <= 3:
                continue
            cursor.execute(
                "SELECT * FROM products WHERE LOWER(name) LIKE LOWER(?)",
                (f"%{clean_word}%",)
            )
            product = cursor.fetchone()
            if product:
                break

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

# ── NEW: save one chat exchange ────────────────────────────────────────────────
def save_chat_history(question, ai_response, platform="website"):
    """Save a customer question and the AI reply to the database."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO chat_history(question, ai_response, platform)
    VALUES (?, ?, ?)
    """, (question, ai_response, platform))

    conn.commit()
    conn.close()

# ── NEW: retrieve all chat history (for admin view) ───────────────────────────
def get_all_chat_history():
    """Return all chat history rows, newest first."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM chat_history ORDER BY timestamp DESC"
    )

    rows = cursor.fetchall()
    conn.close()

    return rows

def initialize_database():

    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        email    TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role     TEXT NOT NULL
    )
    """)

    # Products table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products(
        id    INTEGER PRIMARY KEY AUTOINCREMENT,
        name  TEXT    NOT NULL,
        stock INTEGER NOT NULL,
        price REAL    NOT NULL
    )
    """)

    # ── NEW: Chat history table ────────────────────────────────────────────────
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history(
        id          INTEGER  PRIMARY KEY AUTOINCREMENT,
        question    TEXT     NOT NULL,
        ai_response TEXT     NOT NULL,
        platform    TEXT     NOT NULL DEFAULT 'website',
        timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
