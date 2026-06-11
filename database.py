import sqlite3
import re
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE = "store.db"


def get_connection():
    return sqlite3.connect(DATABASE)


# ── Auth ───────────────────────────────────────────────────────────────────────

def create_default_admin():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE role='seller'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users(email, password, role) VALUES (?, ?, ?)",
            ("admin@store.com", generate_password_hash("admin123"), "seller")
        )
        conn.commit()
    conn.close()

def create_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users(email, password, role) VALUES (?, ?, ?)",
        (email, generate_password_hash(password), "buyer")
    )
    conn.commit()
    conn.close()

def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def verify_user(email, password):
    user = get_user_by_email(email)
    if not user:
        return None
    if check_password_hash(user[2], password):
        return user
    return None


# ── Products ───────────────────────────────────────────────────────────────────
# Column order: id | name | category | stock | price | image_url

def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY name")
    products = cursor.fetchall()
    conn.close()
    return products

def get_product_by_id(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id=?", (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product

def search_product(query):
    conn = get_connection()
    cursor = conn.cursor()

    # 1st try: full phrase
    cursor.execute(
        "SELECT * FROM products WHERE LOWER(name) LIKE LOWER(?)",
        (f"%{query}%",)
    )
    product = cursor.fetchone()

    # 2nd try: word by word
    if not product:
        for word in query.split():
            clean = re.sub(r'[^\w]', '', word)
            if len(clean) <= 3:
                continue
            cursor.execute(
                "SELECT * FROM products WHERE LOWER(name) LIKE LOWER(?)",
                (f"%{clean}%",)
            )
            product = cursor.fetchone()
            if product:
                break

    conn.close()
    return product

def add_product(name, category, stock, price, image_url=None, description=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products(name, category, stock, price, image_url, description) VALUES (?, ?, ?, ?, ?, ?)",
        (name, category, int(stock), float(price), image_url, description)
    )
    conn.commit()
    conn.close()

def update_product(product_id, name, category, stock, price, image_url=None, description=None):
    conn = get_connection()
    cursor = conn.cursor()
    if image_url is not None:
        # New image uploaded — update image too
        cursor.execute(
            "UPDATE products SET name=?, category=?, stock=?, price=?, image_url=?, description=? WHERE id=?",
            (name, category, int(stock), float(price), image_url, description, product_id)
        )
    else:
        # No new image — keep existing image_url, update everything else including description
        cursor.execute(
            "UPDATE products SET name=?, category=?, stock=?, price=?, description=? WHERE id=?",
            (name, category, int(stock), float(price), description, product_id)
        )
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()


# ── Chat history ───────────────────────────────────────────────────────────────

def save_chat_history(question, ai_response, platform="website", session_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_history(question, ai_response, platform, session_id) VALUES (?, ?, ?, ?)",
        (question, ai_response, platform, session_id)
    )
    conn.commit()
    conn.close()

def get_all_chat_history():
    conn = get_connection()
    cursor = conn.cursor()
    # Returns: id[0] question[1] ai_response[2] platform[3] session_id[4] timestamp[5]
    cursor.execute("""
        SELECT id, question, ai_response, platform, session_id, timestamp
        FROM chat_history
        ORDER BY session_id, timestamp DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_buyers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, role FROM users WHERE role='buyer' ORDER BY id DESC")
    buyers = cursor.fetchall()
    conn.close()
    return buyers

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM categories")
    total_categories = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE role='buyer'")
    total_buyers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM chat_history")
    total_chats = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM chat_history WHERE platform='website'")
    web_chats = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM chat_history WHERE platform='telegram'")
    tg_chats = cursor.fetchone()[0]

    cursor.execute("""
        SELECT id, question, ai_response, platform, session_id, timestamp
        FROM chat_history ORDER BY timestamp DESC LIMIT 5
    """)
    recent_chats = cursor.fetchall()

    cursor.execute("SELECT * FROM products WHERE stock <= 5 ORDER BY stock ASC")
    low_stock = cursor.fetchall()

    conn.close()

    return {
        'total_products'  : total_products,
        'total_categories': total_categories,
        'total_buyers'    : total_buyers,
        'total_chats'     : total_chats,
        'web_chats'       : web_chats,
        'tg_chats'        : tg_chats,
        'recent_chats'    : recent_chats,
        'low_stock'       : low_stock,
    }


# ── Categories ─────────────────────────────────────────────────────────────────

def get_all_categories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_category(name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO categories(name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def delete_category(category_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categories WHERE id=?", (category_id,))
    conn.commit()
    conn.close()

def update_category(category_id, new_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE categories SET name=? WHERE id=?", (new_name, category_id))
    conn.commit()
    conn.close()


# ── Database init ──────────────────────────────────────────────────────────────

DEFAULT_CATEGORIES = [
    'Laptop', 'Desktop', 'Monitor', 'Keyboard', 'Mouse',
    'Headset & Audio', 'Storage', 'Networking',
    'Mobile Accessories', 'Components', 'Cables & Adapters', 'Other'
]

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        email    TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role     TEXT NOT NULL
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products(
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT    NOT NULL,
        category    TEXT    NOT NULL DEFAULT 'Other',
        stock       INTEGER NOT NULL,
        price       REAL    NOT NULL,
        image_url   TEXT,
        description TEXT
    )""")

    # Add description to existing databases that don't have it yet
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN description TEXT")
    except Exception:
        pass  # column already exists — safe to ignore

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history(
        id          INTEGER  PRIMARY KEY AUTOINCREMENT,
        question    TEXT     NOT NULL,
        ai_response TEXT     NOT NULL,
        platform    TEXT     NOT NULL DEFAULT 'website',
        session_id  TEXT,
        timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    # Add session_id to existing databases
    try:
        cursor.execute("ALTER TABLE chat_history ADD COLUMN session_id TEXT")
    except Exception:
        pass  # already exists

    # Categories table — pre-populated with defaults on first run
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories(
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )""")

    for cat in DEFAULT_CATEGORIES:
        cursor.execute("INSERT OR IGNORE INTO categories(name) VALUES (?)", (cat,))

    conn.commit()
    conn.close()