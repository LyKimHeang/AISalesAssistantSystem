from flask import Flask, render_template, request, redirect
import sqlite3

admin = Flask(__name__)

# ---------------------------
# VIEW ALL PRODUCTS (READ)
# ---------------------------
@admin.route('/admin')
def index():

    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    conn.close()

    return render_template('admin.html', products=products)


# ---------------------------
# ADD PRODUCT (CREATE)
# ---------------------------
@admin.route('/add', methods=['POST'])
def add():

    name = request.form['name']
    stock = request.form['stock']
    price = request.form['price']

    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO products (name, stock, price) VALUES (?, ?, ?)",
        (name, stock, price)
    )

    conn.commit()
    conn.close()

    return redirect('/admin')


# ---------------------------
# DELETE PRODUCT
# ---------------------------
@admin.route('/delete/<int:id>')
def delete(id):

    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM products WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    return redirect('/admin')


# ---------------------------
# EDIT PRODUCT PAGE
# ---------------------------
@admin.route('/edit/<int:id>')
def edit_page(id):

    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE id = ?", (id,))
    product = cursor.fetchone()

    conn.close()

    return render_template('edit.html', product=product)


# ---------------------------
# UPDATE PRODUCT
# ---------------------------
@admin.route('/update/<int:id>', methods=['POST'])
def update(id):

    name = request.form['name']
    stock = request.form['stock']
    price = request.form['price']

    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products
        SET name = ?, stock = ?, price = ?
        WHERE id = ?
    """, (name, stock, price, id))

    conn.commit()
    conn.close()

    return redirect('/admin')


if __name__ == '__main__':
    admin.run(debug=True, port=5001)