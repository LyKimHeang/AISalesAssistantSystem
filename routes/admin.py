from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session
)

from dotenv import load_dotenv
import os

load_dotenv()

from database import (
    get_all_products,
    add_product,
    delete_product,
    get_product_by_id,
    update_product
)

admin_bp = Blueprint('admin', __name__)


# READ
@admin_bp.route('/admin')
def admin_page():

    if session.get('role') != 'seller':
        return redirect('/login')
    
    products = get_all_products()

    return render_template(
        'admin.html',
        products=products
    )


# CREATE
@admin_bp.route('/add', methods=['POST'])
def add():

    if session.get('role') != 'seller':
        return redirect('/login')
    
    name = request.form['name']
    stock = request.form['stock']
    price = request.form['price']

    add_product(name, stock, price)

    return redirect('/admin')


# DELETE
@admin_bp.route('/delete/<int:id>')
def delete(id):

    if session.get('role') != 'seller':
        return redirect('/login')
    
    delete_product(id)

    return redirect('/admin')


# EDIT PAGE
@admin_bp.route('/edit/<int:id>')
def edit(id):

    if session.get('role') != 'seller':
        return redirect('/login')
    
    product = get_product_by_id(id)

    return render_template(
        'edit.html',
        product=product
    )


# UPDATE
@admin_bp.route('/update/<int:id>', methods=['POST'])
def update(id):

    if session.get('role') != 'seller':
        return redirect('/login')

    name = request.form['name']
    stock = request.form['stock']
    price = request.form['price']

    update_product(
        id,
        name,
        stock,
        price
    )

    return redirect('/admin')