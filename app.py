from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():

    result = None
    message = None

    if request.method == 'POST':

        product = request.form['product']

        conn = sqlite3.connect('store.db')
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM products WHERE LOWER(name) LIKE LOWER(?)",
            (f"%{product}%",)
        )

        result = cursor.fetchone()
        conn.close()

        if result is None:
            message = "❌ Product not found"
        else:
            message = "✅ Product found"

    return render_template('index.html', result=result, message=message)

@app.route('/add', methods=['POST'])
def add_product():

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

    return "Product added successfully! <a href='/'>Go back</a>"

if __name__ == '__main__':
    app.run(debug=True)