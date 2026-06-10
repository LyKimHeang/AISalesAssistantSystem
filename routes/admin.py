import os
import uuid
from flask import Blueprint, render_template, request, redirect, session, current_app
from database import (
    get_all_products, add_product, delete_product,
    get_product_by_id, update_product,
    get_all_categories, add_category, delete_category, update_category,
    get_all_chat_history, get_all_buyers, get_stats
)

admin_bp = Blueprint('admin', __name__)
ALLOWED = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def save_image(file):
    if not file or not file.filename:
        return None
    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in ALLOWED:
        return None
    filename = f"{uuid.uuid4().hex}.{ext}"
    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    return filename

def delete_old_image(image_url):
    if not image_url:
        return
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_url)
    if os.path.exists(path):
        os.remove(path)

def seller_only():
    return session.get('role') != 'seller'


# ── Admin pages ────────────────────────────────────────────────────────────────

@admin_bp.route('/admin')
def admin_overview():
    if seller_only(): return redirect('/login')
    return render_template('admin.html', active='overview', stats=get_stats())

@admin_bp.route('/admin/products')
def admin_products():
    if seller_only(): return redirect('/login')
    return render_template('admin_products.html', active='products',
        products=get_all_products(), categories=get_all_categories())

@admin_bp.route('/admin/chats')
def admin_chats():
    if seller_only(): return redirect('/login')
    return render_template('admin_chats.html', active='chats',
        chats=get_all_chat_history())

@admin_bp.route('/admin/buyers')
def admin_buyers():
    if seller_only(): return redirect('/login')
    return render_template('admin_buyers.html', active='buyers',
        buyers=get_all_buyers())


# ── Product CRUD ───────────────────────────────────────────────────────────────

@admin_bp.route('/add', methods=['POST'])
def add():
    if seller_only(): return redirect('/login')
    description = request.form.get('description', '').strip() or None
    add_product(request.form['name'], request.form['category'],
                request.form['stock'], request.form['price'],
                save_image(request.files.get('image')), description)
    return redirect('/admin/products')

@admin_bp.route('/delete/<int:id>')
def delete(id):
    if seller_only(): return redirect('/login')
    product = get_product_by_id(id)
    if product: delete_old_image(product[5])
    delete_product(id)
    return redirect('/admin/products')

@admin_bp.route('/edit/<int:id>')
def edit(id):
    if seller_only(): return redirect('/login')
    return render_template('edit.html', active='products',
        product=get_product_by_id(id), categories=get_all_categories())

@admin_bp.route('/update/<int:id>', methods=['POST'])
def update(id):
    if seller_only(): return redirect('/login')
    new_image = save_image(request.files.get('image'))
    if new_image:
        old = get_product_by_id(id)
        if old: delete_old_image(old[5])
    description = request.form.get('description', '').strip() or None
    update_product(id, request.form['name'], request.form['category'],
                   request.form['stock'], request.form['price'], new_image, description)
    return redirect('/admin/products')


# ── Category CRUD ──────────────────────────────────────────────────────────────

@admin_bp.route('/categories/add', methods=['POST'])
def category_add():
    if seller_only(): return redirect('/login')
    name = request.form.get('category_name', '').strip()
    if name: add_category(name)
    return redirect('/admin/products?modal=categories')

@admin_bp.route('/categories/delete/<int:id>')
def category_delete(id):
    if seller_only(): return redirect('/login')
    delete_category(id)
    return redirect('/admin/products?modal=categories')

@admin_bp.route('/categories/update/<int:id>', methods=['POST'])
def category_update(id):
    if seller_only(): return redirect('/login')
    new_name = request.form.get('new_name', '').strip()
    if new_name: update_category(id, new_name)
    return redirect('/admin/products?modal=categories')